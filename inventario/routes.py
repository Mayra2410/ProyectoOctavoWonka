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
    # FILTRO: Solo traer productos activos
    productos = Producto.query.filter_by(activo=True).all()

    alertas = []
    for p in productos:
        stock = getattr(p, "stock_actual", 0)
        minimo = getattr(p, "stock_minimo", 10)
        if stock <= minimo:
            alertas.append({
                "producto": p.nombre,
                "actual": stock,
                "mensaje": f"Nivel crítico: Solo quedan {stock} unidades.",
            })

    return render_template(
        "inventario/productoterminado.html", productos=productos, alertas=alertas
    )

@inventario.route("/registrar-ajuste", methods=["POST"])
@login_required
def registrar_ajuste():
    id_prod = request.form.get("producto_id")
    cantidad_input = request.form.get("cantidad", type=int) or 0
    presentacion = request.form.get("presentacion", "PIEZA")
    motivo = request.form.get("motivo", "Ajuste manual")

    multiplicador = {"PIEZA": 1, "MEDIA": 6, "DOCENA": 12}.get(presentacion, 1)
    cantidad_total_piezas = cantidad_input * multiplicador

    producto = Producto.query.get(id_prod)
    if not producto:
        flash("Error: Producto no encontrado.", "danger")
        return redirect(url_for("inventario.mostrar_inventario"))
    
    if not producto.activo:
        flash(f"Error: El producto '{producto.nombre}' está inactivo y no admite movimientos.", "danger")
        return redirect(url_for("inventario.mostrar_inventario"))

    try:
        
        if cantidad_total_piezas > 0:
            receta = Receta.query.filter_by(producto_id=id_prod, activo=True).first()
            
            if not receta:
                flash(f"Aviso: No hay receta activa para {producto.nombre}. Se agregará stock sin descontar insumos.", "warning")
            else:
                detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
                factor_receta = Decimal(str(cantidad_total_piezas))

                for item in detalles:
                    insumo = MateriasPrimas.query.get(item.materia_prima_id)
                    necesario = Decimal(str(item.cantidad_necesaria)) * factor_receta
                    
                    if insumo.stock_actual < necesario:
                        raise Exception(f"Insumo insuficiente: {insumo.nombre} (Faltan {necesario - insumo.stock_actual:.2f})")
                    
                    insumo.stock_actual -= necesario

        stock_proyectado = producto.stock_actual + cantidad_total_piezas
        if stock_proyectado < 0:
             raise Exception(f"No hay suficiente stock de {producto.nombre} para retirar {abs(cantidad_total_piezas)} unidades.")
             
        producto.stock_actual = stock_proyectado

        nuevo_mov = MovimientoInventario(
            producto_id=id_prod,
            tipo_movimiento="AJUSTE",
            cantidad=cantidad_total_piezas,
            motivo=f"{motivo} ({presentacion})",
            usuario_id=session.get("username", "Admin_Wonka"),
            fecha_movimiento=datetime.now(),
        )
        db.session.add(nuevo_mov)

        db.session.commit()
        flash(f"¡Ajuste exitoso! Se procesaron {cantidad_total_piezas} piezas de {producto.nombre}.", "success")

    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        if "INACTIVOS" in error_msg.upper():
            flash("La base de datos bloqueó el ajuste: El producto está marcado como Inactivo.", "danger")
        elif "Insumo insuficiente" in error_msg:
            flash(error_msg, "warning")
        else:
            flash(f"Error en el proceso: {error_msg}", "danger")
            print(f"DEBUG: {error_msg}") # Para ver el error real en consola

    return redirect(url_for("inventario.mostrar_inventario"))