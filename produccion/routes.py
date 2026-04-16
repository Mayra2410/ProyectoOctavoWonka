from flask import render_template, redirect, url_for, flash, session, request
from . import produccion
from models import (
    db,
    OrdenProduccion,
    Producto,
    Receta,
    RecetaDetalle,
    MateriasPrimas,
    Venta,
)
from datetime import datetime
import random
import math
from decimal import Decimal
from utils import login_required

# --- VISTA PRINCIPAL ---
@produccion.route("/ordenes", methods=["GET", "POST"])
@login_required
def mostrar_ordenes():
    query = request.args.get("q") or request.form.get("q")
    consulta = OrdenProduccion.query.join(Producto)

    if query:
        ordenes = consulta.filter(
            (OrdenProduccion.lote.like(f"%{query}%"))
            | (Producto.nombre.like(f"%{query}%"))
            | (OrdenProduccion.id_orden_produccion.like(f"%{query}%"))
        ).all()
    else:
        ordenes = consulta.order_by(OrdenProduccion.id_orden_produccion.desc()).all()

    return render_template("produccion/ordenes.html", ordenes=ordenes)

# --- CREAR ORDEN MANUAL ---
@produccion.route("/crear-orden", methods=["POST"])
@login_required
def crear_orden():
    id_prod = request.form.get("producto_id")
    cant = int(request.form.get("cantidad"))
    prioridad = request.form.get("prioridad", "MEDIA")

    fecha_hoy = datetime.now().strftime("%Y%m%d")
    num_lote = random.randint(100, 999)
    nuevo_lote = f"LOTE-{fecha_hoy}-{num_lote}"

    nueva_orden = OrdenProduccion(
        producto_id=id_prod,
        cantidad_requerida=cant,
        lote=nuevo_lote,
        prioridad=prioridad,
        estado="PENDIENTE",
        fecha_inicio=datetime.now(),
        usuario_inicio=session.get("username", "Admin_Sistema"),
    )

    db.session.add(nueva_orden)
    db.session.commit()
    return redirect(url_for("produccion.mostrar_ordenes"))

# --- PASO 1: SURTIR INSUMOS (PROCESAR MATERIA PRIMA) ---
@produccion.route("/surtir-insumos/<int:id>")
@login_required
def surtir_insumos_orden(id):
    orden = OrdenProduccion.query.get_or_404(id)
    producto = Producto.query.get(orden.producto_id)
    receta = Receta.query.filter_by(producto_id=orden.producto_id, activo=True).first()

    if not receta:
        flash("No hay receta activa.", "danger")
        return redirect(url_for("produccion.mostrar_ordenes"))

    # 1. VALIDACIÓN DETALLADA DE MATERIA PRIMA
    detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
    faltantes = []
    
    for item in detalles:
        materia = MateriasPrimas.query.get(item.materia_prima_id)
        
        # CÁLCULO EXACTO: (Cantidad de la receta * Cantidad de la orden) / Cantidad que rinde el lote
        # Esto nos da exactamente cuánto chocolate, azúcar o leche necesitamos para ESTA orden específica.
        necesario = Decimal(str((float(item.cantidad_necesaria) * float(orden.cantidad_requerida)) / float(receta.cantidad_lote)))
        
        if materia.stock_actual < necesario:
            diferencia = necesario - materia.stock_actual
            # Guardamos el nombre, la cantidad faltante y la unidad (kg, gr, lts)
            faltantes.append(f"{materia.nombre}: faltan {diferencia:.2f} {materia.unidad_medida}")

    if faltantes:
        # Aquí es donde ocurre la magia: mandamos la lista completa al flash
        mensaje_error = " PRODUCCIÓN BLOQUEADA. Lista de compras necesaria: " + " | ".join(faltantes)
        flash(mensaje_error, "danger")
        
        # También lo guardamos en observaciones para que el cliente lo sepa (opcional)
        orden.observaciones = "BLOQUEADO: Esperando insumos específicos."
        db.session.commit()
        
        return redirect(url_for("produccion.mostrar_ordenes"))

    # --- RESTO DEL CÓDIGO (Si no faltan insumos, procedemos a descontar) ---
    for item in detalles:
        materia = MateriasPrimas.query.get(item.materia_prima_id)
        necesario = Decimal(str((float(item.cantidad_necesaria) * float(orden.cantidad_requerida)) / float(receta.cantidad_lote)))
        materia.stock_actual -= necesario

    # Cálculo de tiempo (lo que ya tenías)
    tiempo_base = producto.tiempo_produccion_minutos or 10
    num_lotes = math.ceil(orden.cantidad_requerida / receta.cantidad_lote)
    tiempo_total = num_lotes * tiempo_base

    orden.estado = 'EN_PROCESO'
    orden.observaciones = f"En preparación. Tiempo estimado: {tiempo_total} min."
    
    db.session.commit()
    flash(f" ¡Insumos surtidos con éxito! Tiempo de producción: {tiempo_total} min.", "success")
    return redirect(url_for("produccion.mostrar_ordenes"))

# --- PASO 2: COMPLETAR (PRODUCTO TERMINADO) ---
@produccion.route("/completar-orden/<int:id>")
@login_required
def completar_orden(id):
    orden = OrdenProduccion.query.get_or_404(id)
    
    # Seguridad: No procesar si ya está completada
    if orden.estado == "COMPLETADA":
        return redirect(url_for("produccion.mostrar_ordenes"))

    # Seguridad de flujo: Debe estar EN_PROCESO (surtida)
    if orden.estado != 'EN_PROCESO':
        flash(" Primero debe 'Surtir Insumos' para procesar los ingredientes.", "warning")
        return redirect(url_for("produccion.mostrar_ordenes"))

    producto = Producto.query.get(orden.producto_id)
    
    # Si es manual, sumamos a bodega de producto terminado
    if "AUTO-" not in orden.lote:
        producto.stock_actual += orden.cantidad_requerida
    
    # Finalización de auditoría
    orden.estado = "COMPLETADA"
    orden.fecha_fin = datetime.now()
    orden.usuario_fin = session.get("username")
    orden.observaciones = "¡Pedido terminado y listo para entrega!"

    # Sincronización automática con la Venta para el Corte de Caja
    if "AUTO-" in orden.lote:
        try:
            id_venta = int(orden.lote.split("-")[1])
            v_asociada = Venta.query.get(id_venta)
            if v_asociada:
                v_asociada.estado = "COMPLETADA"
        except:
            pass

    db.session.commit()
    flash(f"✨ ¡Lote {orden.lote} de {producto.nombre} finalizado!", "success")
    return redirect(url_for("produccion.mostrar_ordenes"))