from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import datetime
from .forms import PagoProveedorForm
from models import db, ComprasMateriaPrima, PagoProveedor, MateriasPrimas

pagosProveedores = Blueprint("pagosProveedores", __name__)


@pagosProveedores.route("/pagos-proveedores")
def lista_pagos():
    compras_pendientes = ComprasMateriaPrima.query.filter_by(
        estatus_compra="PENDIENTE"
    ).all()

    return render_template(
        "pagosProveedores/listaPagos.html", compras=compras_pendientes
    )


@pagosProveedores.route("/pagos-proveedores/<int:id_compra>", methods=["GET", "POST"])
def gestionar_pago(id_compra):
    compra = ComprasMateriaPrima.query.get_or_404(id_compra)

    if compra.estatus_compra != "PENDIENTE":
        flash("Esta compra ya fue procesada.", "warning")
        return redirect(url_for("pagosProveedores.lista_pagos"))

    form = PagoProveedorForm()

    if form.validate_on_submit():
        try:
            if form.accion.data == "PAGADO":
                if not form.metodo_pago.data:
                    flash("Selecciona un método de pago.", "warning")
                    return render_template(
                        "pagosProveedores/gestionarPago.html", form=form, compra=compra
                    )

                monto_total = compra.cantidad * compra.costo_unitario

                pago = PagoProveedor(
                    compra_id=compra.id_compra,
                    proveedor_id=compra.proveedor_id,
                    fecha_pago=datetime.now(),
                    monto=monto_total,
                    metodo_pago=form.metodo_pago.data,
                    numero_comprobante=form.numero_comprobante.data,
                    observaciones=form.observaciones.data,
                    usuario_registro="admin",
                )

                db.session.add(pago)

                compra.estatus_compra = "PAGADO"

                materia = MateriasPrimas.query.get(compra.materia_prima_id)
                if materia:
                    # Sumamos al stock lo que se compró
                    materia.stock_actual = (materia.stock_actual or 0) + compra.cantidad
                    materia.costo_unitario = compra.costo_unitario
                    materia.fecha_ultima_compra = datetime.now().date()

                db.session.commit()
                flash("Pago registrado y stock actualizado correctamente.", "success")
                return redirect(url_for("pagosProveedores.lista_pagos"))

            elif form.accion.data == "CANCELADO":
                compra.estatus_compra = "CANCELADO"
                db.session.commit()
                flash("Compra cancelada correctamente.", "info")
                return redirect(url_for("pagosProveedores.lista_pagos"))

        except Exception as e:
            db.session.rollback()
            print(f"Error en pagosProveedores: {e}")
            flash(f"Error al procesar el pago: {str(e)}", "danger")

    # Para depurar si el formulario no valida
    if request.method == "POST" and not form.validate():
        print("Errores del formulario:", form.errors)

    return render_template(
        "pagosProveedores/gestionarPago.html", form=form, compra=compra
    )
