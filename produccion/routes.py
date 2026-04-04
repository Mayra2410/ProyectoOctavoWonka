from flask import render_template, redirect, url_for, flash, session, request
from . import produccion
from models import db, OrdenProduccion, Producto, Receta, RecetaDetalle, MateriaPrima
from datetime import datetime
import random 

@produccion.route('/ordenes')
def mostrar_ordenes():
    if not session.get('username'):
        flash("Por favor, regístrate como administrador.", "warning")
        return redirect(url_for('index'))
    
    query = request.args.get('q') 
    
    if query:
        ordenes = OrdenProduccion.query.filter(
            (OrdenProduccion.lote.like(f"%{query}%")) | 
            (OrdenProduccion.id_orden_produccion == query)
        ).all()
    else:
        ordenes = OrdenProduccion.query.order_by(OrdenProduccion.id_orden_produccion.desc()).all()
        
    return render_template('produccion/ordenes.html', ordenes=ordenes)
@produccion.route('/crear-orden', methods=['POST'])
def crear_orden():
    if session.get('rol') != 'ADMIN':
        flash("Acceso denegado: Solo el Jefe de Producción puede generar órdenes.", "danger")
        return redirect(url_for('produccion.mostrar_ordenes'))

    id_prod = request.form.get('producto_id')
    cant = int(request.form.get('cantidad'))
    prioridad = request.form.get('prioridad', 'MEDIA')

    fecha_hoy = datetime.now().strftime('%Y%m%d')
    num_lote = random.randint(100, 999)
    nuevo_lote = f"LOTE-{fecha_hoy}-{num_lote}"

    nueva_orden = OrdenProduccion(
        producto_id=id_prod,
        cantidad_requerida=cant,
        lote=nuevo_lote,
        prioridad=prioridad,
        estado='PENDIENTE',
        fecha_inicio=datetime.now(),
        usuario_inicio=session.get('username', 'Admin_Sistema') 
    )

    db.session.add(nueva_orden)
    db.session.commit()
    
    flash(f"Orden {nuevo_lote} generada exitosamente.", "success")
    return redirect(url_for('produccion.mostrar_ordenes'))

@produccion.route('/completar-orden/<int:id>')
def completar_orden(id):
    if session.get('rol') != 'ADMIN':
        flash("No tienes permisos para finalizar esta operación.", "danger")
        return redirect(url_for('produccion.mostrar_ordenes'))

    orden = OrdenProduccion.query.get_or_404(id)
    
    if orden.estado == 'COMPLETADA':
        flash("Esta orden ya fue finalizada.", "warning")
        return redirect(url_for('produccion.mostrar_ordenes'))

    receta = Receta.query.filter_by(producto_id=orden.producto_id, activo=True).first()
    if not receta:
        flash(f"Error: No existe receta activa para este producto.", "danger")
        return redirect(url_for('produccion.mostrar_ordenes'))

    detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
    
    for item in detalles:
        insumo = MateriaPrima.query.get(item.materia_prima_id)
        cantidad_necesaria = (item.cantidad_necesaria * orden.cantidad_requerida) / receta.cantidad_lote
        
        if insumo.stock_actual < cantidad_necesaria:
            flash(f"No se puede finalizar: Falta {insumo.nombre}.", "danger")
            return redirect(url_for('produccion.mostrar_ordenes'))

    for item in detalles:
        insumo = MateriaPrima.query.get(item.materia_prima_id)
        cantidad_necesaria = (item.cantidad_necesaria * orden.cantidad_requerida) / receta.cantidad_lote
        insumo.stock_actual -= cantidad_necesaria

    producto = Producto.query.get(orden.producto_id)
    if hasattr(producto, 'stock_actual'):
        producto.stock_actual += orden.cantidad_requerida

    orden.estado = 'COMPLETADA'
    orden.fecha_fin = datetime.now()
    orden.usuario_fin = session.get('username', 'Admin_Sistema')

    db.session.commit()
    flash(f"¡Éxito! Lote {orden.lote} enviado a Inventario.", "success")
    return redirect(url_for('produccion.mostrar_ordenes'))