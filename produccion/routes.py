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


@produccion.route("/ordenes", methods=["GET", "POST"])
def mostrar_ordenes():
    # if not session.get('username'):
    #     flash("Por favor, regístrate.", "warning")
    #     return redirect(url_for('index'))

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

    flash(f"Orden {nuevo_lote} generada exitosamente.", "success")
    return redirect(url_for("produccion.mostrar_ordenes"))


@produccion.route("/completar-orden/<int:id>")
def completar_orden(id):

    orden = OrdenProduccion.query.get_or_404(id)
    if orden.estado == "COMPLETADA":
        return redirect(url_for("produccion.mostrar_ordenes"))

    receta = Receta.query.filter_by(producto_id=orden.producto_id, activo=True).first()
    if not receta:
        flash("Sin receta activa.", "danger")
        return redirect(url_for("produccion.mostrar_ordenes"))

    detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
    for item in detalles:
        insumo = MateriasPrimas.query.get(item.materia_prima_id)
        cantidad_necesaria = (
            item.cantidad_necesaria * orden.cantidad_requerida
        ) / receta.cantidad_lote
        if insumo.stock_actual < cantidad_necesaria:
            faltante = float(cantidad_necesaria) - float(insumo.stock_actual)
            flash(
                f"Falta {faltante:.2f} {insumo.unidad_medida} de {insumo.nombre}.",
                "danger",
            )
            return redirect(url_for("produccion.mostrar_ordenes"))

    for item in detalles:
        insumo = MateriasPrimas.query.get(item.materia_prima_id)
        cantidad_necesaria = (
            item.cantidad_necesaria * orden.cantidad_requerida
        ) / receta.cantidad_lote
        insumo.stock_actual -= cantidad_necesaria

    producto = Producto.query.get(orden.producto_id)
    producto.stock_actual += orden.cantidad_requerida

    orden.estado = "COMPLETADA"
    orden.fecha_fin = datetime.now()
    orden.usuario_fin = session.get("username")

    if "AUTO-" in orden.lote:
        try:
            id_venta = int(orden.lote.split("-")[1])
            otras = OrdenProduccion.query.filter(
                OrdenProduccion.lote.like(f"AUTO-{id_venta}-%"),
                OrdenProduccion.estado == "PENDIENTE",
                OrdenProduccion.id_orden_produccion != id,
            ).first()

            if not otras:
                v_asociada = Venta.query.get(id_venta)
                if v_asociada:
                    v_asociada.estado = "COMPLETADA"
        except:
            pass

    db.session.commit()
    flash(f"Lote {orden.lote} terminado.", "success")
    return redirect(url_for("produccion.mostrar_ordenes"))
