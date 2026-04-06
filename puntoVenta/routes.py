from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Producto, Venta, OrdenProduccion
from datetime import datetime

puntoVenta_bp = Blueprint('puntoVenta', __name__)

@puntoVenta_bp.route('/')
def index():
    productos = Producto.query.filter_by(activo=True).all()
    if 'carrito' not in session:
        session['carrito'] = []
    
    total_carrito = sum(item['subtotal'] for item in session['carrito'])
    return render_template('puntoVenta/pos.html', productos=productos, total=total_carrito)

@puntoVenta_bp.route('/agregar-al-carrito', methods=['POST'])
def agregar():
    id_p = request.form.get('producto_id')
    presentacion = int(request.form.get('presentacion')) 
    cantidad_cajas = int(request.form.get('cantidad_cajas', 1))
    
    prod = Producto.query.get(id_p)
    if prod:
        precio_caja = float(prod.precio_venta) * presentacion
        subtotal = precio_caja * cantidad_cajas
        
        carrito = session.get('carrito', [])
        carrito.append({
            'id': prod.id_producto,
            'nombre': prod.nombre,
            'presentacion': 'Docena' if presentacion == 12 else 'Media Docena',
            'piezas_totales': presentacion * cantidad_cajas,
            'cantidad_cajas': cantidad_cajas,
            'subtotal': subtotal
        })
        session['carrito'] = carrito
        session.modified = True
        
    return redirect(url_for('puntoVenta.index'))

@puntoVenta_bp.route('/quitar-del-carrito/<int:indice>')
def quitar_item(indice):
    carrito = session.get('carrito', [])
    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        session['carrito'] = carrito
        session.modified = True
    return redirect(url_for('puntoVenta.index'))

@puntoVenta_bp.route('/limpiar-carrito')
def limpiar():
    session.pop('carrito', None)
    return redirect(url_for('puntoVenta.index'))

@puntoVenta_bp.route('/finalizar-venta', methods=['POST'])
def finalizar_venta():
    carrito = session.get('carrito', [])
    if not carrito:
        return redirect(url_for('puntoVenta.index'))

    metodo_pago = request.form.get('metodo_pago')
    total_venta = sum(item['subtotal'] for item in carrito)

    try:
        nueva_venta = Venta(
            total=total_venta,
            metodo_pago=metodo_pago,
            fecha_venta=datetime.now(),
            estado='COMPLETADA' 
        )
        db.session.add(nueva_venta)
        db.session.flush()

        session['ultimo_carrito'] = carrito

        for item in carrito:
            prod = Producto.query.get(item['id'])
            piezas_pedidas = item['piezas_totales']

            if prod.stock_actual >= piezas_pedidas:
                prod.stock_actual -= piezas_pedidas
            else:
                tiempo_base = getattr(prod, 'tiempo_preparacion', 20) 
                tiempo_total = (piezas_pedidas / 6) * tiempo_base

                nueva_orden = OrdenProduccion(
                    producto_id=prod.id_producto,
                    cantidad_requerida=int(piezas_pedidas),
                    lote=f"AUTO-{nueva_venta.id_venta}-{prod.id_producto}", 
                    prioridad='URGENTE',
                    estado='PENDIENTE',
                    fecha_inicio=datetime.now(),
                    usuario_inicio="Sistema Ventas",
                    observaciones=f"Faltante Venta #{nueva_venta.id_venta}. Tiempo est. producción: {tiempo_total:.0f} min."
                )
                db.session.add(nueva_orden)
                nueva_venta.estado = 'PENDIENTE'

        db.session.commit()
        session.pop('carrito', None)
        return redirect(url_for('gesVentas.ver_ticket', id=nueva_venta.id_venta))
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
        return redirect(url_for('puntoVenta.index'))