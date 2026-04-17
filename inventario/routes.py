from flask import render_template, request, redirect, url_for, flash, session
from . import inventario
from models import db, Producto, MovimientoInventario
from models import MateriasPrimas, Producto, MovimientoInventario, db
from datetime import datetime
from utils import login_required
from decimal import Decimal
from flask import flash, redirect, url_for, session, request
from models import db, Producto, Receta, RecetaDetalle, MateriasPrimas, MovimientoInventario
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
    # 1. Captura de datos del formulario
    id_prod = request.form.get("producto_id")
    cantidad_input = int(request.form.get("cantidad") or 0)
    presentacion = request.form.get("presentacion")
    motivo = request.form.get("motivo")

    # 2. Conversión a unidades individuales (piezas)
    multiplicador = {"PIEZA": 1, "MEDIA": 6, "DOCENA": 12}.get(presentacion, 1)
    cantidad_total_piezas = cantidad_input * multiplicador
    
    producto = Producto.query.get(id_prod)
    if not producto:
        flash(" Error: Producto no encontrado.", "danger")
        return redirect(url_for("inventario.mostrar_inventario"))

    # 3. LÓGICA DE DESCUENTO DE MATERIA PRIMA (Solo si es una entrada de producto)
    if cantidad_total_piezas > 0:
        receta = Receta.query.filter_by(producto_id=id_prod, activo=True).first()
        
        if not receta:
            flash(f" No hay receta activa para {producto.nombre}. No se puede calcular el gasto de materia prima.", "danger")
            return redirect(url_for("inventario.mostrar_inventario"))

        detalles = RecetaDetalle.query.filter_by(receta_id=receta.id_receta).all()
        faltantes = []

        # CÁLCULO BASADO EN DOCENA:
        # Si la receta es para 12 y estamos metiendo 6 piezas, el factor es 0.5
        factor_receta = Decimal(str(cantidad_total_piezas)) / Decimal("12")

        # Primera pasada: Validar si hay suficiente stock de TODO
        for item in detalles:
            insumo = MateriasPrimas.query.get(item.materia_prima_id)
            necesario = Decimal(str(item.cantidad_necesaria)) * factor_receta

            if insumo.stock_actual < necesario:
                diferencia = necesario - insumo.stock_actual
                faltantes.append(f"{insumo.nombre} (Faltan {diferencia:.2f} {insumo.unidad_medida})")

        if faltantes:
            flash(" AJUSTE CANCELADO. Materia prima insuficiente: " + ", ".join(faltantes), "danger")
            return redirect(url_for("inventario.mostrar_inventario"))

        # Segunda pasada: Descontar ingredientes oficialmente
        for item in detalles:
            insumo = MateriasPrimas.query.get(item.materia_prima_id)
            necesario = Decimal(str(item.cantidad_necesaria)) * factor_receta
            insumo.stock_actual -= necesario

    # 4. VALIDACIÓN DE SALIDA (No quedar en números rojos)
    if (producto.stock_actual + cantidad_total_piezas) < 0:
        flash(" Error: No puedes retirar más producto del que existe en bodega.", "danger")
        return redirect(url_for("inventario.mostrar_inventario"))

    # 5. ACTUALIZACIÓN FINAL
    producto.stock_actual += cantidad_total_piezas

    nuevo_mov = MovimientoInventario(
        producto_id=id_prod,
        tipo_movimiento="AJUSTE",
        cantidad=cantidad_total_piezas,
        motivo=f"{motivo} ({presentacion} - Materia Prima Procesada)",
        usuario_id=session.get("username", "Admin_Wonka"),
        fecha_movimiento=datetime.now()
    )

    try:
        db.session.add(nuevo_mov)
        db.session.commit()
        flash(f" Ajuste exitoso. Inventario actualizado y materia prima descontada.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f" Error al guardar en la base de datos: {str(e)}", "danger")

    return redirect(url_for("inventario.mostrar_inventario"))