from . import compras_bp
from models import ComprasMateriaPrima, MateriasPrimas, Proveedores, db
from flask import render_template, redirect, request, url_for
from . import forms


@compras_bp.route("/compras")
def lista_compras():
    compras = ComprasMateriaPrima.query.all()
    return render_template(
        "comprasProveedores/comprasProveedoresAdmin.html", compras=compras
    )


@compras_bp.route("/compras/registrar", methods=["GET", "POST"])
def registrar_compra():
    form = forms.CompraMateriaPrimaForm(
        request.form if request.method == "POST" else None
    )

    form.materia_prima_id.choices = [
        (m.id_materia_prima, m.nombre) for m in MateriasPrimas.query.all()
    ]
    form.proveedor_id.choices = [
        (p.id_proveedor, p.nombre) for p in Proveedores.query.all()
    ]

    if request.method == "POST" and form.validate():
        nueva_compra = ComprasMateriaPrima(
            materia_prima_id=form.materia_prima_id.data,
            proveedor_id=form.proveedor_id.data,
            cantidad=form.cantidad.data,
            costo_unitario=form.costo_unitario.data,
            fecha_compra=form.fecha_compra.data,
            observaciones=form.observaciones.data,
        )

        try:
            db.session.add(nueva_compra)
            db.session.commit()
            return redirect(url_for("comprasProveedores.lista_compras"))
        except Exception as e:
            db.session.rollback()
            print(f"Error en transacción Wonka: {e}")

    return render_template("comprasProveedores/registrarCompra.html", form=form)


@compras_bp.route("/compras/detalles/<int:id>")
def detalles_compra(id):
    compra = ComprasMateriaPrima.query.get_or_404(id)

    meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    return render_template(
        "comprasProveedores/detallesComprasProveedores.html", compra=compra, meses=meses
    )