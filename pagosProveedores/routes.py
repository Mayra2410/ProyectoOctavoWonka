from flask import Blueprint, render_template, redirect, url_for, flash, request
from datetime import datetime
from .forms import PagoProveedorForm
from models import db, ComprasMateriaPrima, PagoProveedor, MateriasPrimas
from utils import login_required


pagosProveedores = Blueprint("pagosProveedores", __name__)


@pagosProveedores.route("/pagos-proveedores")
@login_required
def lista_pagos():
    compras_pendientes = ComprasMateriaPrima.query.filter_by(
        estatus_compra="PENDIENTE"
    ).all()

    return render_template(
        "pagosProveedores/listaPagos.html", compras=compras_pendientes
    )


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
                # La validación del método de pago ya la hace tu form, 
                # así que aquí vamos directo al grano.
                monto_total = compra.cantidad * compra.costo_unitario

                pago = PagoProveedor(
                    compra_id=compra.id_compra,
                    proveedor_id=compra.proveedor_id,
                    fecha_pago=datetime.now(),
                    monto=monto_total,
                    metodo_pago=form.metodo_pago.data,
                    # numero_comprobante ELIMINADO
                    observaciones=form.observaciones.data,
                    usuario_registro="admin",
                )

                db.session.add(pago)
                compra.estatus_compra = "PAGADO"

                materia = MateriasPrimas.query.get(compra.materia_prima_id)
                if materia:
                    materia.stock_actual = (materia.stock_actual or 0) + compra.cantidad
                    materia.costo_unitario = compra.costo_unitario
                    materia.fecha_ultima_compra = datetime.now().date()

                db.session.commit()
                flash("Pago registrado y stock actualizado correctamente.", "success")
                return redirect(url_for("pagosProveedores.lista_pagos"))

            elif form.accion.data == "CANCELADO":
                # Como tu validador en forms.py ya prohíbe cancelar si hay método de pago,
                # si llegamos aquí es porque los datos son correctos.
                compra.estatus_compra = "CANCELADO"
                db.session.commit()
                flash("Compra cancelada correctamente.", "info")
                return redirect(url_for("pagosProveedores.lista_pagos"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar el pago: {str(e)}", "danger")

    # --- CRUCIAL: Esto atrapa los errores de validación de tu forms.py ---
    if request.method == "POST" and not form.validate():
        for field, errors in form.errors.items():
            for error in errors:
                # Esto enviará el mensaje "No debes seleccionar método si vas a cancelar"
                flash(error, "danger") 

    return render_template(
        "pagosProveedores/gestionarPago.html", form=form, compra=compra
    )