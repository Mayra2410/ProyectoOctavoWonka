from flask import render_template, request, redirect, url_for, flash, session
from . import inventario
from models import db, Producto, MovimientoInventario
from models import MateriasPrimas, Producto, MovimientoInventario, db
from datetime import datetime
from utils import login_required
from decimal import Decimal
from flask import flash, redirect, url_for, session, request
from models import (
    db,
    Producto,
    Receta,
    RecetaDetalle,
    MateriasPrimas,
    MovimientoInventario,
)
from datetime import datetime


@inventario.route("/producto-terminado")
@login_required
def mostrar_inventario():
    productos = Producto.query.all()

    alertas = []
    for p in productos:
        stock = getattr(p, "stock_actual", 0)
        minimo = getattr(p, "stock_minimo", 10)

        if stock <= minimo:
            alertas.append(
                {
                    "producto": p.nombre,
                    "actual": stock,
                    "mensaje": f"Nivel crítico: Solo quedan {stock} unidades.",
                }
            )

    return render_template(
        "inventario/productoterminado.html", productos=productos, alertas=alertas
    )


@inventario.route("/registrar-ajuste", methods=["POST"])
@login_required
def registrar_ajuste():
    id_prod = request.form.get("producto_id")
    cantidad_input = int(request.form.get("cantidad") or 0)
    presentacion = request.form.get("presentacion")
    motivo = request.form.get("motivo")

    multiplicador = {"PIEZA": 1, "MEDIA": 6, "DOCENA": 12}.get(presentacion, 1)
    cantidad_total_piezas = cantidad_input * multiplicador

    producto = Producto.query.get(id_prod)
    if not producto:
        flash(" Error: Producto no encontrado.", "danger")
        return redirect(url_for("inventario.mostrar_inventario"))

    if cantidad_total_piezas > 0:
        receta = Receta.query.filter_by(producto_id=id_prod, activo=True).first()

        if not receta:
            flash(
                f" No hay receta activa para {producto.nombre}. No se descontará materia prima.",
                "warning",
            )
        else:
            detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
            faltantes = []

            factor_receta = Decimal(str(cantidad_total_piezas))

            for item in detalles:
                insumo = MateriasPrimas.query.get(item.materia_prima_id)
                # cantidad_necesaria (por pieza) * total de piezas
                necesario = Decimal(str(item.cantidad_necesaria)) * factor_receta

                if insumo.stock_actual < necesario:
                    diferencia = necesario - insumo.stock_actual
                    faltantes.append(
                        f"{insumo.nombre} (Faltan {diferencia:.4f} {insumo.unit_medida if hasattr(insumo, 'unit_medida') else 'uds'})"
                    )

            if faltantes:
                flash(
                    " AJUSTE CANCELADO. Materia prima insuficiente: "
                    + ", ".join(faltantes),
                    "danger",
                )
                return redirect(url_for("inventario.mostrar_inventario"))

            for item in detalles:
                insumo = MateriasPrimas.query.get(item.materia_prima_id)
                necesario = Decimal(str(item.cantidad_necesaria)) * factor_receta
                insumo.stock_actual -= necesario

    if (producto.stock_actual + cantidad_total_piezas) < 0:
        flash(
            " Error: No puedes retirar más producto del que existe en bodega.", "danger"
        )
        return redirect(url_for("inventario.mostrar_inventario"))

    producto.stock_actual += cantidad_total_piezas

    nuevo_mov = MovimientoInventario(
        producto_id=id_prod,
        tipo_movimiento="AJUSTE",
        cantidad=cantidad_total_piezas,
        motivo=f"{motivo} ({presentacion})",
        usuario_id=session.get("username", "Admin_Wonka"),
        fecha_movimiento=datetime.now(),
    )

    try:
        db.session.add(nuevo_mov)
        db.session.commit()
        flash(
            f" Ajuste exitoso. Se procesaron {cantidad_total_piezas} piezas y se descontaron sus insumos.",
            "success",
        )
    except Exception as e:
        db.session.rollback()
        flash(f" Error al guardar: {str(e)}", "danger")

    return redirect(url_for("inventario.mostrar_inventario"))
