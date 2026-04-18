from . import compras_bp
from models import ComprasMateriaPrima, MateriasPrimas, Proveedores, db
from flask import render_template, redirect, request, url_for, flash
from . import forms
from utils import login_required


@compras_bp.route("/compras")
@login_required
def lista_compras():
    compras = ComprasMateriaPrima.query.all()
    return render_template(
        "comprasProveedores/comprasProveedoresAdmin.html", compras=compras
    )


@compras_bp.route("/compras/registrar", methods=["GET", "POST"])
@login_required
def registrar_compra():
    # FILTRO: Solo traemos Materias Primas y Proveedores con estatus activo
    materias_query = MateriasPrimas.query.filter_by(activo=True).all()
    proveedores_query = Proveedores.query.filter_by(activo=True).all()

    form = forms.CompraMateriaPrimaForm(
        request.form if request.method == "POST" else None
    )

    # Llenamos las opciones del formulario con los resultados filtrados
    form.materia_prima_id.choices = [(0, "SELECCIONA UN INSUMO")] + [
        (m.id_materia_prima, m.nombre) for m in materias_query
    ]
    form.proveedor_id.choices = [(0, "SELECCIONA UN PROVEEDOR")] + [
        (p.id_proveedor, p.nombre) for p in proveedores_query
    ]

    if request.method == "POST" and form.validate():
        # Verificamos que la materia prima exista y esté activa antes de proceder
        materia = MateriasPrimas.query.filter_by(id_materia_prima=form.materia_prima_id.data, activo=True).first()

        if not materia:
            flash("La materia prima seleccionada no es válida o está inactiva.", "danger")
            return redirect(url_for("comprasProveedores.registrar_compra"))

        nueva_compra = ComprasMateriaPrima(
            materia_prima_id=form.materia_prima_id.data,
            proveedor_id=form.proveedor_id.data,
            cantidad=form.cantidad.data,
            costo_unitario=form.costo_unitario.data,
            fecha_compra=form.fecha_compra.data,
            observaciones=form.observaciones.data,
            estatus_compra="PENDIENTE", #
        )

        try:
            # Actualizamos datos en la tabla de materia prima basándonos en la compra
            materia.costo_unitario = form.costo_unitario.data
            materia.fecha_ultima_compra = form.fecha_compra.data

            db.session.add(nueva_compra)
            db.session.commit()

            return redirect(url_for("comprasProveedores.lista_compras"))

        except Exception as e:
            db.session.rollback()
            print(f"Error en transacción Wonka: {e}")
            flash("Ocurrió un error al registrar la compra.", "danger")

    return render_template(
        "comprasProveedores/registrarCompra.html", form=form, materias=materias_query
    )


@compras_bp.route("/compras/detalles/<int:id>")
@login_required
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
