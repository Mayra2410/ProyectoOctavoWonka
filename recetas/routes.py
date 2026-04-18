from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from . import recetas
from .forms import RecetaForm
from models import db, Receta, Producto, MateriasPrimas, RecetaDetalle
from utils import login_required


@recetas.route("/recetas")
@login_required
def lista_recetas():
    busqueda = request.args.get("q", "").strip()
    query = Receta.query

    if busqueda:
        query = query.filter(Receta.nombre_receta.ilike(f"%{busqueda}%"))

    lista_recetas = query.order_by(Receta.id_receta.asc()).all()

    return render_template(
        "recetas/recetasAdmin.html",
        recetas=lista_recetas,
        busqueda=busqueda,
        active_page="recetas.lista_recetas",
    )


@recetas.route("/recetas/agregar", methods=["GET", "POST"])
@login_required
def agregar_receta():
    form = RecetaForm()

    productos_libres = (
        Producto.query.outerjoin(Receta, Producto.id_producto == Receta.producto_id)
        .filter(Producto.activo == True)
        .filter(Receta.id_receta == None)
        .all()
    )
    form.producto_id.choices = [(p.id_producto, p.nombre) for p in productos_libres]

    if form.validate_on_submit():
        nombre_limpio = form.nombre_receta.data.strip()

        if Receta.query.filter_by(nombre_receta=nombre_limpio).first():
            form.nombre_receta.errors.append("Esta receta ya existe.")
            return render_template("recetas/agregarReceta.html", form=form)

        nueva_receta = Receta(
            producto_id=form.producto_id.data,
            nombre_receta=nombre_limpio,
            instrucciones=(
                form.instrucciones.data.strip() if form.instrucciones.data else None
            ),
        )

        try:
            db.session.add(nueva_receta)
            db.session.commit()
            flash("Receta agregada correctamente.", "success")
            return redirect(
                url_for(
                    "recetas.gestionar_ingredientes", id_receta=nueva_receta.id_receta
                )
            )

        except IntegrityError:
            db.session.rollback()
            flash("Error: El producto ya tiene una receta asignada.", "danger")

        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            if "cancelada" in error_msg or "INACTIVO" in error_msg:
                flash("No puedes crear recetas para productos inactivos.", "warning")
            else:
                flash("Ocurrió un error inesperado al guardar.", "danger")
                print(f"Error real: {e}")

    return render_template(
        "recetas/agregarReceta.html", form=form, active_page="recetas.lista_recetas"
    )


@recetas.route("/recetas/editar/<int:id_receta>", methods=["GET", "POST"])
@login_required
def modificar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    form = RecetaForm(request.form if request.method == "POST" else None, obj=receta)

    productos_disponibles = (
        Producto.query.outerjoin(Receta, Producto.id_producto == Receta.producto_id)
        .filter(Producto.activo == True)
        .filter(
            (Receta.id_receta == None) | (Producto.id_producto == receta.producto_id)
        )
        .all()
    )
    form.producto_id.choices = [
        (p.id_producto, p.nombre) for p in productos_disponibles
    ]

    if request.method == "POST" and form.validate():
        receta.producto_id = form.producto_id.data
        receta.nombre_receta = form.nombre_receta.data.strip()
        receta.instrucciones = (
            form.instrucciones.data.strip() if form.instrucciones.data else None
        )

        estado_valor = request.form.get("activo")
        receta.activo = True if estado_valor == "1" else False

        try:
            db.session.commit()
            flash("Receta actualizada correctamente.", "success")
            return redirect(url_for("recetas.lista_recetas"))

        except Exception as e:
            db.session.rollback()
            if "INACTIVO" in str(e):
                flash(
                    "Error: No puedes asignar esta receta a un producto inactivo.",
                    "danger",
                )
            else:
                flash("Error al actualizar la receta.", "danger")

    if request.method == "GET":
        form.activo.data = receta.activo

    return render_template(
        "recetas/modificarReceta.html",
        form=form,
        receta=receta,
        active_page="recetas.lista_recetas",
    )


@recetas.route("/recetas/desactivar/<int:id_receta>", methods=["POST"])
@login_required
def desactivar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    receta.activo = False
    try:
        db.session.commit()
        flash("Receta desactivada correctamente.", "warning")
    except Exception:
        db.session.rollback()
        flash("Error al desactivar.", "danger")
    return redirect(url_for("recetas.lista_recetas"))


@recetas.route("/recetas/reactivar/<int:id_receta>", methods=["POST"])
@login_required
def reactivar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    receta.activo = True
    try:
        db.session.commit()
        flash("Receta reactivada correctamente.", "success")
    except Exception:
        db.session.rollback()
        flash("Error al reactivar.", "danger")
    return redirect(url_for("recetas.lista_recetas"))


@recetas.route("/recetas/detalles/<int:id_receta>")
@login_required
def detalle_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    return render_template(
        "recetas/detallesRecetas.html",
        receta=receta,
        active_page="recetas.lista_recetas",
    )


@recetas.route("/recetas/<int:id_receta>/ingredientes", methods=["GET", "POST"])
@login_required
def gestionar_ingredientes(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    materias = MateriasPrimas.query.filter_by(activo=True).all()
    form = FlaskForm()

    if request.method == "POST":
        materia_id = request.form.get("materia_prima_id", type=int)
        cantidad_cap = request.form.get("cantidad_necesaria", type=float)
        unidad_cap = request.form.get("unidad_receta")

        materia = MateriasPrimas.query.get_or_404(materia_id)
        cantidad_base = cantidad_cap

        if unidad_cap == "g" and materia.unidad_medida.lower() == "kg":
            cantidad_base = cantidad_cap / 1000
        elif unidad_cap == "mg" and materia.unidad_medida.lower() == "kg":
            cantidad_base = cantidad_cap / 1000000
        elif unidad_cap == "ml" and materia.unidad_medida.lower() == "lt":
            cantidad_base = cantidad_cap / 1000

        nuevo_detalle = RecetaDetalle(
            receta_id=id_receta,
            materia_prima_id=materia_id,
            cantidad_necesaria=cantidad_base,
            cantidad_capturada=cantidad_cap,
            unidad_capturada=unidad_cap,
            unidad_medida=materia.unidad_medida,
        )

        try:
            db.session.add(nuevo_detalle)
            db.session.commit()
            flash("Ingrediente agregado.", "success")
        except Exception as e:
            db.session.rollback()
            print(f"Error al agregar ingrediente: {e}")
            flash("Error al guardar ingrediente.", "danger")

        return redirect(url_for("recetas.gestionar_ingredientes", id_receta=id_receta))

    return render_template(
        "recetas/ingredientesReceta.html", receta=receta, materias=materias, form=form
    )


@recetas.route("/recetas/ingrediente/eliminar/<int:id_detalle>", methods=["POST"])
@login_required
def eliminar_ingrediente(id_detalle):
    detalle = RecetaDetalle.query.get_or_404(id_detalle)
    id_receta = detalle.receta_id

    try:
        db.session.delete(detalle)
        db.session.commit()
        flash("Ingrediente quitado de la receta.", "info")
    except Exception:
        db.session.rollback()
        flash("No se pudo quitar el ingrediente.", "danger")

    return redirect(url_for("recetas.gestionar_ingredientes", id_receta=id_receta))


@recetas.route("/recetas/eliminar/confirmar/<int:id_receta>")
@login_required
def confirmar_eliminar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    form = FlaskForm()

    return render_template(
        "recetas/eliminarReceta.html",
        receta=receta,
        form=form,
        receta_id=id_receta,
        active_page="recetas.lista_recetas",
    )
