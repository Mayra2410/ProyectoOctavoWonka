from flask import render_template, redirect, url_for, flash, session, request
from . import produccion
from models import db, OrdenProduccion, Producto, Receta, RecetaDetalle, MateriasPrimas, Venta
from datetime import datetime
import random 
from decimal import Decimal
from utils import login_required


@produccion.route('/ordenes', methods=['GET', 'POST']) 
@login_required
def mostrar_ordenes():
    # if not session.get('username'):
    #     flash("Por favor, regístrate.", "warning")
    #     return redirect(url_for('index'))
    
    query = request.args.get('q') or request.form.get('q')
    
    consulta = OrdenProduccion.query.join(Producto)
    
    if query:
        ordenes = consulta.filter(
            (OrdenProduccion.lote.like(f"%{query}%")) | 
            (Producto.nombre.like(f"%{query}%")) |
            (OrdenProduccion.id_orden_produccion.like(f"%{query}%"))
        ).all()
    else:
        ordenes = consulta.order_by(OrdenProduccion.id_orden_produccion.desc()).all()
        
    return render_template('produccion/ordenes.html', ordenes=ordenes)
@produccion.route('/crear-orden', methods=['POST'])
@login_required
def crear_orden():

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

from decimal import Decimal
from datetime import datetime

@produccion.route('/completar-orden/<int:id>')
@login_required
def completar_orden(id):
    orden = OrdenProduccion.query.get_or_404(id)
    if orden.estado == 'COMPLETADA':
        return redirect(url_for('produccion.mostrar_ordenes'))

    receta = Receta.query.filter_by(producto_id=orden.producto_id, activo=True).first()
    if not receta:
        flash("Error: No hay una receta activa para fabricar este chocolate.", "danger")
        return redirect(url_for('produccion.mostrar_ordenes'))

    detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
    faltantes = []

    for item in detalles:
        materia = MateriasPrimas.query.get(item.materia_prima_id)
        necesario = Decimal(str((float(item.cantidad_necesaria) * float(orden.cantidad_requerida)) / float(receta.cantidad_lote)))
        
        if materia.stock_actual < necesario:
            diferencia = necesario - materia.stock_actual
            faltantes.append(f"{materia.nombre} (Faltan: {diferencia:.2f} {materia.unidad_medida})")

    if faltantes:
        flash(" PRODUCCIÓN BLOQUEADA. Faltan insumos: " + ", ".join(faltantes), "danger")
        return redirect(url_for('produccion.mostrar_ordenes'))

    for item in detalles:
        materia = MateriasPrimas.query.get(item.materia_prima_id)
        necesario = Decimal(str((float(item.cantidad_necesaria) * float(orden.cantidad_requerida)) / float(receta.cantidad_lote)))
        materia.stock_actual -= necesario

    producto = Producto.query.get(orden.producto_id)
    if "AUTO-" not in orden.lote:
        producto.stock_actual += orden.cantidad_requerida
    
    orden.estado = 'COMPLETADA'
    orden.fecha_fin = datetime.now()
    orden.usuario_fin = session.get('username')

    if "AUTO-" in orden.lote:
        try:
            id_venta = int(orden.lote.split('-')[1])
            v_asociada = Venta.query.get(id_venta)
            if v_asociada:
                v_asociada.estado = 'COMPLETADA'
                flash(f"¡Venta #{id_venta} surtida y completada!", "success")
        except:
            pass

    db.session.commit()
    flash(f"Lote {orden.lote} finalizado correctamente.", "success")
    return redirect(url_for('produccion.mostrar_ordenes'))