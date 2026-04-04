from flask import render_template, request, redirect, url_for, flash, session
from . import gesVentas
from models import db, Producto, Venta, OrdenProduccion, Cliente, PagoProveedor
from datetime import datetime
from sqlalchemy import func

@gesVentas.route('/gestion-ventas')
def mostrar_ventas():
    query = request.args.get('q') 
    
    if query:
        ventas = Venta.query.filter(Venta.id_venta == query).all()
    else:
        ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    
    hoy = datetime.now().date()
    ingresos = db.session.query(func.sum(Venta.total)).filter(func.date(Venta.fecha_venta) == hoy, Venta.estado == 'COMPLETADA').scalar() or 0
    egresos = db.session.query(func.sum(PagoProveedor.monto)).filter(func.date(PagoProveedor.fecha_pago) == hoy).scalar() or 0
    utilidad = ingresos - egresos
    productos_db = db.session.query(Producto.id_producto, Producto.nombre, Producto.precio_venta).all()
    
    return render_template('gesVentas/gestVentas.html', 
                           ventas=ventas, ingresos=ingresos, egresos=egresos, 
                           utilidad=utilidad, productos=productos_db, hoy=hoy)

@gesVentas.route('/ver-ticket/<int:id>')
def ver_ticket(id):
    venta = Venta.query.get_or_404(id)
    return render_template('gesVentas/ticket.html', venta=venta)

@gesVentas.route('/corte-caja')
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
    
    return render_template('gesVentas/corte.html', 
                           ingresos=ingresos, 
                           egresos=egresos, 
                           utilidad=utilidad,
                           hoy=hoy.strftime('%d/%m/%Y'))