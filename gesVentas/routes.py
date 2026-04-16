from flask import render_template, request, redirect, url_for, flash, session
from . import gesVentas
from models import db, Producto, Venta, OrdenProduccion, Cliente, PagoProveedor, DetalleVenta
from datetime import datetime
from sqlalchemy import func
from utils import login_required

# --- 1. GESTIÓN Y LISTADO DE VENTAS ---
# --- RUTAS DE GESTIÓN DE VENTAS ---

@gesVentas.route('/gestion-ventas', methods=['GET', 'POST'])
@login_required
def mostrar_ventas():
    # 1. Definimos la fecha de hoy para los filtros
    hoy = datetime.now().date()

    # 2. Sincronización: Si producción terminó, la venta pasa a COMPLETADA
    ventas_pendientes = Venta.query.filter(Venta.estado == 'PENDIENTE').all()
    for v in ventas_pendientes:
        # Buscamos si aún existen órdenes que NO estén completadas
        quendan_ordenes = OrdenProduccion.query.filter(
            OrdenProduccion.lote.like(f"AUTO-{v.id_venta}-%"),
            OrdenProduccion.estado != 'COMPLETADA'
        ).first()
        
        # Si ya no quedan órdenes pendientes, la venta ya se puede entregar
        if not quendan_ordenes:
            v.estado = 'COMPLETADA'
    
    db.session.commit()

    # 3. Lógica del Buscador
    query = request.args.get('q') 
    if query and query.isdigit():
        ventas = Venta.query.filter(Venta.id_venta == int(query)).all()
    else:
        ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    
    # 4. Cálculo de Ingresos (Corregido para sumar COMPLETADAS y ENTREGADAS)
    # Filtramos por 'hoy' para que coincida con el panel de control
    ingresos = db.session.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha_venta) == hoy,
        Venta.estado.in_(['COMPLETADA', 'ENTREGADA']) 
    ).scalar() or 0
    
    # 5. Cálculo de Egresos y Utilidad
    egresos = db.session.query(func.sum(PagoProveedor.monto)).filter(
        func.date(PagoProveedor.fecha_pago) == hoy
    ).scalar() or 0
    
    utilidad = ingresos - egresos
    
    # 6. Renderizado final
    return render_template('gesVentas/gestVentas.html', 
                           ventas=ventas, 
                           ingresos=ingresos, 
                           egresos=egresos, 
                           utilidad=utilidad, 
                           hoy=hoy)

@gesVentas.route('/entregar-venta/<int:id>')
@login_required
def entregar_venta(id):
    venta = Venta.query.get_or_404(id)
    # Solo se puede entregar si ya se fabricó (COMPLETADA)
    if venta.estado == 'COMPLETADA':
        venta.estado = 'ENTREGADA'
        db.session.commit()
        flash(f" Venta #{id} marcada como ENTREGADA al cliente.", "success")
    else:
        flash(" No se puede entregar un producto que no ha terminado producción.", "warning")
    return redirect(url_for('gesVentas.mostrar_ventas'))


# --- 2. CANCELACIÓN DE VENTAS ---
@gesVentas.route('/cancelar-venta/<int:id>')
@login_required
def cancelar_venta(id):
    venta = Venta.query.get_or_404(id)
    # Limpiamos órdenes de producción automáticas asociadas
    OrdenProduccion.query.filter(OrdenProduccion.lote.like(f"AUTO-{id}-%")).delete(synchronize_session=False)
    
    venta.estado = 'CANCELADA'
    db.session.commit()
    flash(f"Venta #{id} cancelada y logística revertida.", "warning")
    return redirect(url_for('gesVentas.mostrar_ventas'))

# --- 3. TICKET DINÁMICO (Lógica de Trazabilidad) ---
@gesVentas.route("/ver-ticket/<int:id>")
@login_required
def ver_ticket(id):
    venta = Venta.query.get_or_404(id)
    
    # Buscamos la orden para saber si está en espera o en horno
    from models import OrdenProduccion
    orden = OrdenProduccion.query.filter(OrdenProduccion.lote.like(f"AUTO-{id}-%")).first()
    
    productos_ticket = session.get('ultimo_carrito', [])
    
    # Plan B: Si la sesión expiró, reconstruimos desde DetalleVenta
    if not productos_ticket:
        detalles = DetalleVenta.query.filter_by(venta_id=id).all()
        for d in detalles:
            prod = Producto.query.get(d.producto_id)
            productos_ticket.append({
                'nombre': prod.nombre,
                'cantidad_cajas': d.cantidad,
                'presentacion': getattr(prod, 'presentacion', 'Pieza'),
                'subtotal': d.subtotal
            })

    ahorro = request.args.get('ahorro', 0)

    return render_template('gesVentas/ticket.html', 
                           venta=venta, 
                           productos=productos_ticket, 
                           ahorro=ahorro,
                           orden=orden)

# --- 4. CORTE DE CAJA PROFESIONAL ---
@gesVentas.route("/corte-caja")
@login_required
def corte_caja():
    # 1. GESTIÓN DE RANGO
    hoy_dt = datetime.now()
    inicio_defecto = hoy_dt.replace(day=1).strftime('%Y-%m-%d')
    fin_defecto = hoy_dt.strftime('%Y-%m-%d')

    fecha_inicio = request.args.get('fecha_inicio', inicio_defecto)
    fecha_fin = request.args.get('fecha_fin', fin_defecto)

    # 2. CÁLCULOS DESDE LA BASE DE DATOS (IMPORTANTE: INCLUIR 'ENTREGADA')
    ingresos = db.session.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha_venta).between(fecha_inicio, fecha_fin),
        Venta.estado.in_(['COMPLETADA', 'ENTREGADA']) # <--- SUMAMOS AMBOS ESTADOS
    ).scalar() or 0

    egresos = db.session.query(func.sum(PagoProveedor.monto)).filter(
        func.date(PagoProveedor.fecha_pago).between(fecha_inicio, fecha_fin)
    ).scalar() or 0

    reserva = float(ingresos) * 0.20
    utilidad = float(ingresos) - float(egresos) - reserva

    # 3. GRÁFICA TOP PRODUCTOS (TAMBIÉN FILTRAR POR AMBOS ESTADOS)
    top_productos = db.session.query(
        Producto.nombre, 
        func.count(Venta.id_venta).label('total_ventas')
    ).join(DetalleVenta, Producto.id_producto == DetalleVenta.producto_id) \
     .join(Venta, DetalleVenta.venta_id == Venta.id_venta) \
     .filter(
         func.date(Venta.fecha_venta).between(fecha_inicio, fecha_fin),
         Venta.estado.in_(['COMPLETADA', 'ENTREGADA']) # <--- PARA QUE LA GRÁFICA NO SALGA VACÍA
     ) \
     .group_by(Producto.nombre) \
     .order_by(func.count(Venta.id_venta).desc()) \
     .limit(5).all()

    labels_prod = [p[0] for p in top_productos]
    values_prod = [int(p[1]) for p in top_productos]

    # 4. TENDENCIA DE VENTAS
    ventas_rango = db.session.query(
        func.date(Venta.fecha_venta).label('dia'), 
        func.sum(Venta.total)
    ).filter(
        func.date(Venta.fecha_venta).between(fecha_inicio, fecha_fin),
        Venta.estado.in_(['COMPLETADA', 'ENTREGADA']) # <--- PARA QUE LA LÍNEA DE TIEMPO SUBA
    ).group_by(func.date(Venta.fecha_venta)).order_by(func.date(Venta.fecha_venta)).all()

    labels_dias = [v[0].strftime('%d/%m') for v in ventas_rango]
    values_dias = [float(v[1]) for v in ventas_rango]

    # 5. MONGO FEEDBACK (Opcional)
    labels_rating, values_rating = [], []
    try:
        from clientes.routesC import get_mongo_db
        db_mongo = get_mongo_db()
        pipeline = [{"$group": {"_id": "$nombre_producto", "promedio": {"$avg": "$calificacion"}}}, {"$sort": {"promedio": -1}}]
        stats = list(db_mongo.resenas_productos.aggregate(pipeline))
        labels_rating = [s['_id'] for s in stats]
        values_rating = [round(s['promedio'], 2) for s in stats]
    except: pass

    # 6. HISTORIAL DE CIERRES
    historial_cortes = []
    try:
        historial_cortes = db.session.execute(
            db.text("SELECT * FROM cortes_caja ORDER BY fecha_registro DESC LIMIT 10")
        ).all()
    except: pass

    return render_template(
        "gesVentas/corte.html",
        ingresos=ingresos, egresos=egresos, reserva=reserva, utilidad=utilidad,
        hoy=hoy_dt.strftime("%d/%m/%Y"), fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        labels_prod=labels_prod, values_prod=values_prod,
        labels_dias=labels_dias, values_dias=values_dias,
        labels_rating=labels_rating, values_rating=values_rating,
        historial_cortes=historial_cortes
    )
# --- 5. PERSISTENCIA DE ARCHIVO CONTABLE ---
@gesVentas.route("/guardar-corte", methods=["POST"])
@login_required
def guardar_corte():
    try:
        sql = """INSERT INTO cortes_caja (fecha_inicio, fecha_fin, total_ingresos, total_egresos, monto_reserva, utilidad_neta)
                 VALUES (:fi, :ff, :ing, :egr, :res, :util)"""
        db.session.execute(db.text(sql), {
            'fi': request.form.get("f_inicio"), 'ff': request.form.get("f_fin"),
            'ing': request.form.get("ingresos"), 'egr': request.form.get("egresos"),
            'res': request.form.get("reserva"), 'util': request.form.get("utilidad")
        })
        db.session.commit()
        flash("¡Ciclo financiero archivado con éxito!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al archivar: {e}", "danger")
    return redirect(url_for('gesVentas.corte_caja'))