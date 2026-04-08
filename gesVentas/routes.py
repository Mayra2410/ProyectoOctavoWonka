from flask import render_template, request, redirect, url_for, flash, session
from . import gesVentas
from models import db, Producto, Venta, OrdenProduccion, Cliente, PagoProveedor
from datetime import datetime
from sqlalchemy import func

@gesVentas.route('/gestion-ventas', methods=['GET', 'POST'])
def mostrar_ventas():
    ventas_pendientes = Venta.query.filter_by(estado='PENDIENTE').all()
    for v in ventas_pendientes:
        quedan_ordenes = OrdenProduccion.query.filter(
            OrdenProduccion.lote.like(f"AUTO-{v.id_venta}-%"),
            OrdenProduccion.estado == 'PENDIENTE'
        ).first()
        
        if not quedan_ordenes:
            v.estado = 'COMPLETADA'
    db.session.commit()

    query = request.args.get('q') 
    if query and query.isdigit():
        ventas = Venta.query.filter(Venta.id_venta == int(query)).all()
    else:
        ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    
    hoy = datetime.now().date()
    ingresos = db.session.query(func.sum(Venta.total)).filter(func.date(Venta.fecha_venta) == hoy, Venta.estado == 'COMPLETADA').scalar() or 0
    egresos = db.session.query(func.sum(PagoProveedor.monto)).filter(func.date(PagoProveedor.fecha_pago) == hoy).scalar() or 0
    utilidad = ingresos - egresos
    
    productos_db = Producto.query.filter_by(activo=True).all()
    
    return render_template('gesVentas/gestVentas.html', 
                           ventas=ventas, ingresos=ingresos, egresos=egresos, 
                           utilidad=utilidad, productos=productos_db, hoy=hoy)

@gesVentas.route('/cancelar-venta/<int:id>')
def cancelar_venta(id):
    venta = Venta.query.get_or_404(id)
    OrdenProduccion.query.filter(OrdenProduccion.lote.like(f"AUTO-{id}-%")).delete(synchronize_session=False)
    
    venta.estado = 'CANCELADA'
    db.session.commit()
    flash(f"Venta #{id} cancelada y sus órdenes de producción eliminadas.", "warning")
    return redirect(url_for('gesVentas.mostrar_ventas'))

@gesVentas.route('/historial-ventas')
def historial_ventas():
    ventas = Venta.query.join(Cliente).order_by(Venta.fecha_venta.desc()).all()
    
    return render_template('gesVentas/historial.html', ventas=ventas)

@gesVentas.route('/ver-ticket/<int:id>')
def ver_ticket(id):
    venta = Venta.query.get_or_404(id)
    productos_ticket = session.get('ultimo_carrito', [])
    return render_template('gesVentas/ticket.html', venta=venta, productos=productos_ticket)

@gesVentas.route("/corte-caja")
def corte_caja():
    hoy = datetime.now().date()
    
    ingresos = db.session.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha_venta) == hoy, 
        Venta.estado == 'COMPLETADA'
    ).scalar() or 0

    egresos = db.session.query(func.sum(PagoProveedor.monto)).filter(
        func.date(PagoProveedor.fecha_pago) == hoy
    ).scalar() or 0

    utilidad = ingresos - egresos

    top_productos = db.session.query(
        Producto.nombre, 
        func.count(Venta.id_venta).label('total_ventas')
    ).join(Venta, Venta.id_venta > 0).group_by(Producto.nombre).order_by(func.count(Venta.id_venta).desc()).limit(5).all()

    labels_prod = [p[0] for p in top_productos]
    values_prod = [int(p[1]) for p in top_productos]

    ventas_semana = db.session.query(
        func.date(Venta.fecha_venta).label('dia'),
        func.sum(Venta.total)
    ).filter(Venta.estado == 'COMPLETADA').group_by(func.date(Venta.fecha_venta)).order_by(func.date(Venta.fecha_venta)).limit(7).all()

    labels_dias = [v[0].strftime('%d/%m') for v in ventas_semana]
    values_dias = [float(v[1]) for v in ventas_semana]

    return render_template(
        "gesVentas/corte.html",
        ingresos=ingresos,
        egresos=egresos,
        utilidad=utilidad,
        hoy=hoy.strftime("%d/%m/%Y"),
        labels_prod=labels_prod,
        values_prod=values_prod,
        labels_dias=labels_dias,
        values_dias=values_dias
    )