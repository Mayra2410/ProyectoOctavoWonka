from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from datetime import datetime
from .forms import PagoProveedorForm
from models import db, ComprasMateriaPrima, PagoProveedor, MateriasPrimas
from utils import login_required


pagosProveedores = Blueprint("pagosProveedores", __name__)


@pagosProveedores.route("/pagos-proveedores")
@login_required
def lista_pagos():
    compras_activas = (
        ComprasMateriaPrima.query.filter(
            ComprasMateriaPrima.estatus_compra.in_(["PENDIENTE", "PAGADO"])
        )
        .order_by(ComprasMateriaPrima.id_compra.desc())
        .all()
    )

    return render_template("pagosProveedores/listaPagos.html", compras=compras_activas)


@pagosProveedores.route("/pagos-proveedores/<int:id_compra>", methods=["GET", "POST"])
@login_required
def gestionar_pago(id_compra):
    compra = ComprasMateriaPrima.query.get_or_404(id_compra)

    if compra.estatus_compra != "PENDIENTE":
        flash("Esta compra ya fue procesada.", "warning")
        return redirect(url_for("pagosProveedores.lista_pagos"))

    form = PagoProveedorForm()

    if form.validate_on_submit():
        try:
            if form.accion.data == "PAGADO":
                monto_total = compra.cantidad * compra.costo_unitario
                pago = PagoProveedor(
                    compra_id=compra.id_compra,
                    proveedor_id=compra.proveedor_id,
                    fecha_pago=datetime.now(),
                    monto=monto_total,
                    metodo_pago=form.metodo_pago.data,
                    observaciones=form.observaciones.data,
                    usuario_registro=session.get("username", "admin"),
                )
                db.session.add(pago)

                compra.estatus_compra = "PAGADO"

                db.session.commit()
                flash("Pago registrado. Pendiente de recibir mercancía.", "success")
                return redirect(url_for("pagosProveedores.lista_pagos"))

            elif form.accion.data == "CANCELADO":
                compra.estatus_compra = "CANCELADO"
                db.session.commit()
                flash("Compra cancelada correctamente.", "info")
                return redirect(url_for("pagosProveedores.lista_pagos"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar el pago: {str(e)}", "danger")

    if request.method == "POST" and not form.validate():
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, "danger")

    return render_template(
        "pagosProveedores/gestionarPago.html", form=form, compra=compra
    )


@pagosProveedores.route("/recibir-materia/<int:id_compra>", methods=["POST"])
@login_required
def recibir_materia(id_compra):
    compra = ComprasMateriaPrima.query.get_or_404(id_compra)

    if compra.estatus_compra != "PAGADO":
        flash("Solo se puede recibir mercancía que ya ha sido pagada.", "warning")
        return redirect(url_for("pagosProveedores.lista_pagos"))

    try:
        materia = MateriasPrimas.query.get(compra.materia_prima_id)
        if materia:
            materia.stock_actual = (materia.stock_actual or 0) + compra.cantidad
            materia.costo_unitario = compra.costo_unitario
            materia.fecha_ultima_compra = datetime.now().date()

            compra.estatus_compra = "RECIBIDO" 
            db.session.commit()
            flash(
                f"¡Mercancía recibida! {compra.cantidad} unidades añadidas al stock.",
                "success",
            )
        else:
            flash("Error: No se encontró la materia prima.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al procesar entrada: {str(e)}", "danger")

    return redirect(url_for("pagosProveedores.lista_pagos"))
