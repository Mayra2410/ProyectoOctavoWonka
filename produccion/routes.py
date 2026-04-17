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


@produccion.route("/surtir-insumos/<int:id>")
@login_required
def surtir_insumos_orden(id):
    orden = OrdenProduccion.query.get_or_404(id)
    producto = Producto.query.get(orden.producto_id)
    receta = Receta.query.filter_by(producto_id=orden.producto_id, activo=True).first()

    if not receta:
        flash("No hay receta activa.", "danger")
        return redirect(url_for("produccion.mostrar_ordenes"))

    detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
    faltantes = []

    factor_receta = Decimal(str(orden.cantidad_requerida))

    for item in detalles:
        materia = MateriasPrimas.query.get(item.materia_prima_id)
        necesario = Decimal(str(item.cantidad_necesaria)) * factor_receta

        if materia.stock_actual < necesario:
            diferencia = necesario - materia.stock_actual
            faltantes.append(
                f"{materia.nombre}: faltan {diferencia:.4f} {materia.unidad_medida}"
            )

    if faltantes:
        flash(
            " PRODUCCIÓN BLOQUEADA. Materia insuficiente: " + " | ".join(faltantes),
            "danger",
        )
        return redirect(url_for("produccion.mostrar_ordenes"))

    for item in detalles:
        materia = MateriasPrimas.query.get(item.materia_prima_id)
        necesario = Decimal(str(item.cantidad_necesaria)) * factor_receta
        materia.stock_actual -= necesario

    tiempo_base = producto.tiempo_produccion_minutos or 10
    num_lotes_tiempo = math.ceil(orden.cantidad_requerida / 12)
    tiempo_total = num_lotes_tiempo * tiempo_base

    orden.estado = "EN_PROCESO"
    orden.observaciones = f"En preparación. Tiempo estimado: {tiempo_total} min."

    db.session.commit()
    flash(
        f" ¡Insumos surtidos! Se descontó materia prima para {orden.cantidad_requerida} piezas.",
        "success",
    )
    return redirect(url_for("produccion.mostrar_ordenes"))


@produccion.route("/completar-orden/<int:id>")
@login_required
def completar_orden(id):
    orden = OrdenProduccion.query.get_or_404(id)

    if orden.estado == "COMPLETADA":
        return redirect(url_for("produccion.mostrar_ordenes"))

    if orden.estado != "EN_PROCESO":
        flash(
            " Primero debe 'Surtir Insumos' para procesar los ingredientes.", "warning"
        )
        return redirect(url_for("produccion.mostrar_ordenes"))

    producto = Producto.query.get(orden.producto_id)

    if "AUTO-" not in orden.lote:
        producto.stock_actual += orden.cantidad_requerida

    orden.estado = "COMPLETADA"
    orden.fecha_fin = datetime.now()
    orden.usuario_fin = session.get("username")
    orden.observaciones = "¡Pedido terminado y listo para entrega!"

    if "AUTO-" in orden.lote:
        try:
            id_venta = int(orden.lote.split("-")[1])
            v_asociada = Venta.query.get(id_venta)
            if v_asociada:
                v_asociada.estado = "COMPLETADA"
        except:
            pass

    db.session.commit()
    flash(f" ¡Lote {orden.lote} de {producto.nombre} finalizado!", "success")
    return redirect(url_for("produccion.mostrar_ordenes"))
