from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, OrdenProduccion, Producto, Venta, Cliente, TarjetaCliente
from datetime import datetime

puntoVenta_bp = Blueprint("puntoVenta", __name__)


@puntoVenta_bp.route("/")
def index():
    productos = Producto.query.filter_by(activo=True).all()
    if "carrito" not in session:
        session["carrito"] = []

    total_carrito = sum(item["subtotal"] for item in session["carrito"])
    return render_template(
        "puntoVenta/pos.html", productos=productos, total=total_carrito
    )


@puntoVenta_bp.route("/agregar-al-carrito", methods=["POST"])
def agregar():
    id_p = request.form.get("producto_id")
    presentacion = int(request.form.get("presentacion"))
    cantidad_cajas = int(request.form.get("cantidad_cajas", 1))

    prod = Producto.query.get(id_p)
    if prod:
        precio_caja = float(prod.precio_venta) * presentacion
        subtotal = precio_caja * cantidad_cajas

        carrito = session.get("carrito", [])
        carrito.append(
            {
                "id": prod.id_producto,
                "nombre": prod.nombre,
                "presentacion": "Docena" if presentacion == 12 else "Media Docena",
                "piezas_totales": presentacion * cantidad_cajas,
                "cantidad_cajas": cantidad_cajas,
                "subtotal": subtotal,
            }
        )
        session["carrito"] = carrito
        session.modified = True

    return redirect(url_for("puntoVenta.index"))


@puntoVenta_bp.route("/quitar-del-carrito/<int:indice>")
def quitar_item(indice):
    carrito = session.get("carrito", [])
    if 0 <= indice < len(carrito):
        carrito.pop(indice)
        session["carrito"] = carrito
        session.modified = True
    return redirect(url_for("puntoVenta.index"))


@puntoVenta_bp.route("/limpiar-carrito")
def limpiar():
    session.pop("carrito", None)
    return redirect(url_for("puntoVenta.index"))


@puntoVenta_bp.route("/registrar-tarjeta", methods=["GET", "POST"])
def registrar_tarjeta_view():
    if request.method == "POST":
        user_id = session.get("user_id")
        cliente = Cliente.query.filter_by(usuario_id=user_id).first()

        if not cliente:
            flash("Error: No se encontró perfil de cliente.", "danger")
            return redirect(url_for("puntoVenta.index"))

        num_tarjeta = request.form.get("numero_tarjeta")
        terminacion = num_tarjeta[-4:] if num_tarjeta else "0000"

        try:
            nueva_tarjeta = TarjetaCliente(
                cliente_id=cliente.id_cliente,
                numero_encriptado="HASH-WONKA-SECURE",
                terminacion=terminacion,
                banco="Banco Wonka Internacional",
            )
            if hasattr(cliente, "tarjeta_registrada"):
                cliente.tarjeta_registrada = True

            db.session.add(nueva_tarjeta)
            db.session.commit()

            flash(f"Tarjeta terminada en {terminacion} vinculada con éxito.", "success")
            return redirect(url_for("puntoVenta.index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar la tarjeta: {e}", "danger")

    return render_template("puntoVenta/registrar_tarjeta.html")


@puntoVenta_bp.route("/finalizar-venta", methods=["POST"])
def finalizar_venta():
    carrito = session.get("carrito", [])
    if not carrito:
        flash("El carrito está vacío", "warning")
        return redirect(url_for("puntoVenta.index"))

    user_id = session.get("user_id")
    if not user_id:
        flash("Debes iniciar sesión para finalizar la compra", "danger")
        return redirect(url_for("index"))

    metodo_pago = request.form.get("metodo_pago")
    total_bruto = sum(item["subtotal"] for item in carrito)

    cliente = Cliente.query.filter_by(usuario_id=user_id).first()

    if metodo_pago == "TARJETA":
        if not cliente:
            flash("Perfil de cliente no encontrado.", "danger")
            return redirect(url_for("puntoVenta.index"))

        tiene_tarjeta = TarjetaCliente.query.filter_by(
            cliente_id=cliente.id_cliente, activa=True
        ).first()

        if not tiene_tarjeta:
            flash("No tienes tarjetas vinculadas. Registra una para continuar.", "info")
            return redirect(url_for("puntoVenta.registrar_tarjeta_view"))

    descuento = 0
    if cliente:
        es_vip = (
            cliente.tipo == "MAYORISTA" or cliente.categoria_comprador == "FRECUENTE"
        )
        if es_vip and total_bruto > 5000:
            descuento = total_bruto * 0.15
            flash(f"¡Descuento VIP Wonka aplicado! Ahorro: ${descuento:.2f}", "success")

    total_final = total_bruto - descuento

    try:
        nueva_venta = Venta(
            cliente_id=cliente.id_cliente if cliente else None,
            total=total_final,
            metodo_pago=metodo_pago,
            fecha_venta=datetime.now(),
            estado="COMPLETADA",
        )
        db.session.add(nueva_venta)
        db.session.flush()

        session["ultimo_carrito"] = carrito

        for item in carrito:
            prod = Producto.query.get(item["id"])
            piezas_pedidas = item["piezas_totales"]

            if prod.stock_actual >= piezas_pedidas:
                prod.stock_actual -= piezas_pedidas
            else:
                nueva_orden = OrdenProduccion(
                    producto_id=prod.id_producto,
                    cantidad_requerida=int(piezas_pedidas),
                    lote=f"AUTO-{nueva_venta.id_venta}-{prod.id_producto}",
                    prioridad="URGENTE",
                    estado="PENDIENTE",
                    fecha_inicio=datetime.now(),
                    observaciones=f"Falta de stock en Venta #{nueva_venta.id_venta}",
                )
                db.session.add(nueva_orden)
                nueva_venta.estado = "PENDIENTE"

        db.session.commit()
        session.pop("carrito", None)

        # Flash de éxito para el cliente
        # flash("¡Compra realizada con éxito! Revisa tu historial de pedidos.", "success")

        return redirect(
            url_for("gesVentas.ver_ticket", id=nueva_venta.id_venta, ahorro=descuento)
        )
    except Exception as e:
        db.session.rollback()
        flash(f"Error crítico: {e}", "danger")
        return redirect(url_for("puntoVenta.index"))
