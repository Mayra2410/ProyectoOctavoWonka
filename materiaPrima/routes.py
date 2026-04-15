import base64
from flask import render_template, redirect, request, url_for, flash
from models import db, MateriasPrimas, Proveedores
from . import materia_Prima
from . import forms
from utils import login_required


@materia_Prima.route("/materias-primas")
@login_required
def admin_materias():
    materias = MateriasPrimas.query.all()
    return render_template("materiaPrima/materiaPrimaAdmin.html", materias=materias)


@materia_Prima.route("/detalles/<int:id>")
@login_required
def detalle_materia(id):
    materia = MateriasPrimas.query.get_or_404(id)
    return render_template("materiaPrima/detallesMateriaPrima.html", materia=materia)


@materia_Prima.route("/agregar", methods=["GET", "POST"])
@login_required
def agregar_materia():
    form = forms.MateriaPrimaForm(request.form)
    form.proveedor_id.choices = [
        (p.id_proveedor, p.nombre) for p in Proveedores.query.all()
    ]

    if form.validate_on_submit():
        file = request.files.get("imagen_materia")
        imagen_base64 = None

        if file and file.filename != "":
            img_bytes = file.read()
            encoded = base64.b64encode(img_bytes).decode("utf-8")
            imagen_base64 = f"data:{file.content_type};base64,{encoded}"

        try:
            nueva_materia = MateriasPrimas(
                nombre=form.nombre.data,
                unidad_medida=form.unidad_medida.data,
                stock_actual=form.stock_actual.data,
                stock_minimo=form.stock_minimo.data,
                costo_unitario=form.costo_unitario.data,
                porcentaje_merma=form.porcentaje_merma.data,
                fecha_ultima_compra=form.fecha_ultima_compra.data,
                proveedor_id=form.proveedor_id.data,
                descripcion=form.descripcion.data,
                imagen_materia=imagen_base64,
                activo=bool(form.activo.data),
            )

            db.session.add(nueva_materia)
            db.session.commit()
            return redirect(url_for("materiaPrima.admin_materias"))

        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar: {e}")
            return render_template(
                "materiaPrima/agregarMateriaPrima.html",
                form=form,
                error_img="Error al guardar.",
            )

    return render_template("materiaPrima/agregarMateriaPrima.html", form=form)


@materia_Prima.route("/modificar/<int:id>", methods=["GET", "POST"])
@login_required
def modificar_materia(id):
    materia = MateriasPrimas.query.get_or_404(id)
    stock_real_db = materia.stock_actual
    form = forms.MateriaPrimaForm(request.form, obj=materia)
    form.proveedor_id.choices = [
        (p.id_proveedor, p.nombre) for p in Proveedores.query.order_by("nombre").all()
    ]

    if request.method == "POST" and form.validate():
        duplicado = MateriasPrimas.query.filter(
            MateriasPrimas.nombre == form.nombre.data,
            MateriasPrimas.id_materia_prima != id,
        ).first()

        if duplicado:
            form.nombre.errors.append("Este nombre de insumo ya está registrado.")
            return render_template(
                "materiaPrima/modificarMateriaPrima.html",
                form=form,
                materia_id=id,
                materia=materia,
            )

        file = request.files.get("imagen_materia")
        if file and file.filename != "":
            imagen_bytes = file.read()
            encoded_string = base64.b64encode(imagen_bytes).decode("utf-8")
            materia.imagen_materia = f"data:{file.content_type};base64,{encoded_string}"

        form.populate_obj(materia)
        
        materia.stock_actual = stock_real_db
        materia.activo = bool(form.activo.data)

        try:
            db.session.commit()
            return redirect(url_for("materiaPrima.admin_materias"))
        except Exception as e:
            db.session.rollback()
            print(f"Error al modificar: {e}")

    return render_template(
        "materiaPrima/modificarMateriaPrima.html",
        form=form,
        materia_id=id,
        materia=materia,
    )


@materia_Prima.route("/materias-primas/eliminar/confirmar/<int:id>")
@login_required
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
@login_required

def desactivar_materia(id):
    materia = MateriasPrimas.query.get_or_404(id)
    materia.activo = False
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(url_for("materiaPrima.admin_materias"))
