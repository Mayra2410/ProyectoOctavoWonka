from flask import render_template, request, redirect, url_for, flash, session
from . import inventario
from models import db, Producto, MovimientoInventario
from models import MateriasPrimas, Producto, MovimientoInventario, db
from datetime import datetime


@inventario.route("/producto-terminado")
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
def registrar_ajuste():
    id_prod = request.form.get("producto_id")
    cantidad_input = int(request.form.get("cantidad"))
    presentacion = request.form.get("presentacion")
    motivo = request.form.get("motivo")

    multiplicador = 1
    if presentacion == "MEDIA":
        multiplicador = 6
    elif presentacion == "DOCENA":
        multiplicador = 12

    cantidad_total_piezas = cantidad_input * multiplicador

    producto = Producto.query.get(id_prod)

    if (producto.stock_actual + cantidad_total_piezas) < 0:
        flash("No puedes retirar más producto del que existe en piezas.", "danger")
        return redirect(url_for("inventario.mostrar_inventario"))

    producto.stock_actual += cantidad_total_piezas

    nuevo_mov = MovimientoInventario(
        producto_id=id_prod,
        tipo_movimiento="AJUSTE",
        cantidad=cantidad_total_piezas,
        motivo=f"{motivo} (Ajuste por {presentacion})",
        usuario_id=session.get("username", "Admin_Mayra"),
    )

    db.session.add(nuevo_mov)
    db.session.commit()
    flash(f"Se ajustaron {abs(cantidad_total_piezas)} piezas correctamente.", "success")
    return redirect(url_for("inventario.mostrar_inventario"))
