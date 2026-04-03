from flask import render_template, redirect, request, url_for, flash
from models import (
    db,
    MateriasPrimas,
    Proveedores,
)
from . import materia_Prima
from . import forms
import base64


# Listado de materias primas
@materia_Prima.route("/materias-primas")
def admin_materias():
    materias = MateriasPrimas.query.all()
    return render_template("materiaPrima/materiaPrimaAdmin.html", materias=materias)


# Detalles de materia prima
@materia_Prima.route("/detalles/<int:id>")
def detalle_materia(id):
    materia = MateriasPrimas.query.get_or_404(id)
    return render_template("materiaPrima/detallesMateriaPrima.html", materia=materia)


@materia_Prima.route("/agregar", methods=["GET", "POST"])
def agregar_materia():
    form = forms.MateriaPrimaForm(request.form)

    form.proveedor_id.choices = [
        (p.id_proveedor, p.nombre) for p in Proveedores.query.order_by("nombre").all()
    ]

    if request.method == "POST" and form.validate():
        existe = MateriasPrimas.query.filter_by(nombre=form.nombre.data).first()
        if existe:
            form.nombre.errors.append("Este insumo ya existe.")
            return render_template("materiaPrima/agregarMateriaPrima.html", form=form)

        nueva_materia = MateriasPrimas(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            unidad_medida=form.unidad_medida.data,
            stock_actual=form.stock_actual.data,
            stock_minimo=form.stock_minimo.data,
            costo_unitario=form.costo_unitario.data,
            proveedor_id=form.proveedor_id.data,
            fecha_ultima_compra=form.fecha_ultima_compra.data,
            porcentaje_merma=form.porcentaje_merma.data,
            activo=bool(form.activo.data),
        )

        file = request.files.get("imagen_materia")
        if file and file.filename != "":
            try:
                import base64

                imagen_bytes = file.read()
                encoded = base64.b64encode(imagen_bytes).decode("utf-8")
                nueva_materia.imagen_materia = (
                    f"data:{file.content_type};base64,{encoded}"
                )
            except Exception as e:
                print(f"Error foto: {e}")

        try:
            db.session.add(nueva_materia)
            db.session.commit()
            return redirect(url_for("materiaPrima.admin_materias"))
        except Exception as e:
            db.session.rollback()
            print(f"Error DB: {e}")

    return render_template("materiaPrima/agregarMateriaPrima.html", form=form)


# Modificar materia prima
@materia_Prima.route("/modificar/<int:id>", methods=["GET", "POST"])
def modificar_materia(id):
    materia = MateriasPrimas.query.get_or_404(id)

    form = forms.MateriaPrimaForm(request.form, obj=materia)

    form.proveedor_id.choices = [
        (p.id_proveedor, p.nombre) for p in Proveedores.query.order_by("nombre").all()
    ]

    if request.method == "POST" and form.validate():

        duplicado_nombre = MateriasPrimas.query.filter(
            MateriasPrimas.nombre == form.nombre.data,
            MateriasPrimas.id_materia_prima != id,
        ).first()

        if duplicado_nombre:
            form.nombre.errors.append("Este nombre de insumo ya está registrado.")
            return render_template(
                "materiaPrima/modificarMateriaPrima.html", form=form, materia_id=id
            )

        file = request.files.get("imagen_materia")
        if file and file.filename != "":
            imagen_bytes = file.read()
            encoded_string = base64.b64encode(imagen_bytes).decode("utf-8")
            materia.imagen_materia = f"data:{file.content_type};base64,{encoded_string}"

        form.populate_obj(materia)

        materia.proveedor_id = form.proveedor_id.data
        materia.activo = bool(form.activo.data)

        try:
            db.session.commit()
            return redirect(url_for("materiaPrima.admin_materias"))
        except Exception as e:
            db.session.rollback()
            return render_template(
                "materiaPrima/modificarMateriaPrima.html", form=form, materia_id=id
            )

    return render_template(
        "materiaPrima/modificarMateriaPrima.html",
        form=form,
        materia_id=id,
        materia=materia,
    )


# Eliminar materia prima (desactiva)
@materia_Prima.route("/materias-primas/eliminar/confirmar/<int:id>")
def eliminar_materia(id):
    materia = MateriasPrimas.query.get_or_404(id)
    form = forms.MateriaPrimaForm()

    return render_template(
        "materiaPrima/eliminarMateriaPrima.html",
        materia=materia,
        form=form,
        materia_id=id,
    )


@materia_Prima.route("/materias-primas/desactivar/<int:id>", methods=["POST"])
def desactivar_materia(id):
    materia = MateriasPrimas.query.get_or_404(id)

    materia.activo = False

    try:
        db.session.commit()
        return redirect(url_for("materiaPrima.admin_materias"))
    except Exception as e:
        db.session.rollback()
        return redirect(url_for("materiaPrima.admin_materias"))
