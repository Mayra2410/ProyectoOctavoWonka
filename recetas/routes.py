from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from . import recetas
from .forms import RecetaForm
from models import db, Receta, Producto, MateriasPrimas, RecetaDetalle
from utils import login_required



@recetas.route('/recetas')
@login_required
def lista_recetas():
    busqueda = request.args.get('q', '').strip()

    query = Receta.query

    if busqueda:
        query = query.filter(Receta.nombre_receta.ilike(f'%{busqueda}%'))

    lista_recetas = query.order_by(Receta.id_receta.asc()).all()

    return render_template(
        'recetas/recetasAdmin.html',
        recetas=lista_recetas,
        busqueda=busqueda,
        active_page='recetas.lista_recetas'
    )


@recetas.route('/recetas/agregar', methods=['GET', 'POST'])
@login_required
def agregar_receta():
    form = RecetaForm()
    form.producto_id.choices = [(p.id_producto, p.nombre) for p in Producto.query.all()]

    if form.validate_on_submit():
        nombre_limpio = form.nombre_receta.data.strip()

        existe_nombre = Receta.query.filter_by(nombre_receta=nombre_limpio).first()
        if existe_nombre:
            form.nombre_receta.errors.append('Esta receta ya existe.')

        existe_producto = Receta.query.filter_by(producto_id=form.producto_id.data).first()
        if existe_producto:
            form.producto_id.errors.append('Ese producto ya tiene una receta registrada.')

        if form.nombre_receta.errors or form.producto_id.errors:
            return render_template(
                'recetas/agregarReceta.html',
                form=form,
                active_page='recetas.lista_recetas'
            )

        nueva_receta = Receta(
            producto_id=form.producto_id.data,
            nombre_receta=nombre_limpio,
            cantidad_lote=form.cantidad_lote.data,
            instrucciones=form.instrucciones.data.strip() if form.instrucciones.data else None,
            activo=bool(int(request.form.get('activo', 1)))
        )

        try:
            db.session.add(nueva_receta)
            db.session.commit()
            flash('Receta agregada correctamente. Ahora agrega sus ingredientes.', 'success')
            return redirect(url_for('recetas.gestionar_ingredientes', id_receta=nueva_receta.id_receta))
        except IntegrityError:
            db.session.rollback()
            form.producto_id.errors.append('Ese producto ya tiene una receta registrada.')
        except Exception:
            db.session.rollback()
            flash('Ocurrió un error al guardar la receta.', 'danger')

    return render_template(
        'recetas/agregarReceta.html',
        form=form,
        active_page='recetas.lista_recetas'
    )


@recetas.route('/recetas/editar/<int:id_receta>', methods=['GET', 'POST'])
@login_required
def modificar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    form = RecetaForm(obj=receta)
    form.producto_id.choices = [(p.id_producto, p.nombre) for p in Producto.query.all()]

    if form.validate_on_submit():
        nombre_limpio = form.nombre_receta.data.strip()

        duplicado_nombre = Receta.query.filter(
            Receta.nombre_receta == nombre_limpio,
            Receta.id_receta != id_receta
        ).first()

        if duplicado_nombre:
            form.nombre_receta.errors.append('Este nombre de receta ya está registrado.')

        duplicado_producto = Receta.query.filter(
            Receta.producto_id == form.producto_id.data,
            Receta.id_receta != id_receta
        ).first()

        if duplicado_producto:
            form.producto_id.errors.append('Ese producto ya tiene una receta registrada.')

        if form.nombre_receta.errors or form.producto_id.errors:
            return render_template(
                'recetas/modificarReceta.html',
                form=form,
                receta=receta,
                active_page='recetas.lista_recetas'
            )

        receta.producto_id = form.producto_id.data
        receta.nombre_receta = nombre_limpio
        receta.cantidad_lote = form.cantidad_lote.data
        receta.instrucciones = form.instrucciones.data.strip() if form.instrucciones.data else None
        receta.activo = bool(int(request.form.get('activo', 1)))

        try:
            db.session.commit()
            flash('Receta actualizada correctamente.', 'success')
            return redirect(url_for('recetas.lista_recetas'))
        except IntegrityError:
            db.session.rollback()
            form.producto_id.errors.append('Ese producto ya tiene una receta registrada.')
        except Exception:
            db.session.rollback()
            flash('Ocurrió un error al actualizar la receta.', 'danger')

    return render_template(
        'recetas/modificarReceta.html',
        form=form,
        receta=receta,
        active_page='recetas.lista_recetas'
    )


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
        active_page='recetas.lista_recetas'
    )


@recetas.route("/recetas/desactivar/<int:id_receta>", methods=["POST"])
@login_required
def desactivar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    receta.activo = False

    try:
        db.session.commit()
        flash('Receta desactivada correctamente.', 'warning')
    except Exception:
        db.session.rollback()
        flash('Ocurrió un error al desactivar la receta.', 'danger')

    return redirect(url_for("recetas.lista_recetas"))


@recetas.route('/recetas/reactivar/<int:id_receta>', methods=['POST'])
@login_required
def reactivar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    receta.activo = True

    try:
        db.session.commit()
        flash('Receta reactivada correctamente.', 'success')
    except Exception:
        db.session.rollback()
        flash('Ocurrió un error al reactivar la receta.', 'danger')

    return redirect(url_for('recetas.lista_recetas'))


@recetas.route('/recetas/detalles/<int:id_receta>')
@login_required
def detalle_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)

    return render_template(
        'recetas/detallesRecetas.html',
        receta=receta,
        active_page='recetas.lista_recetas'
    )


@recetas.route('/recetas/<int:id_receta>/ingredientes', methods=['GET', 'POST'])
@login_required
def gestionar_ingredientes(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    materias = MateriasPrimas.query.filter_by(activo=True).order_by(MateriasPrimas.nombre.asc()).all()
    form = FlaskForm()

    if request.method == 'POST':
        materia_prima_id = request.form.get('materia_prima_id', type=int)
        cantidad_necesaria = request.form.get('cantidad_necesaria', type=float)

        if not materia_prima_id:
            flash('Selecciona una materia prima de la lista.', 'warning')
            return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

        if cantidad_necesaria is None:
            flash('La cantidad necesaria es obligatoria.', 'warning')
            return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

        if cantidad_necesaria <= 0:
            flash('La cantidad debe ser un número mayor a 0. No se permiten valores negativos.', 'danger')
            return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

        materia = MateriasPrimas.query.get_or_404(materia_prima_id)

        existente = RecetaDetalle.query.filter_by(
            receta_id=id_receta,
            materia_prima_id=materia_prima_id
        ).first()

        if existente:
            flash(f'La materia prima "{materia.nombre}" ya está agregada a esta receta.', 'warning')
            return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

        nuevo_detalle = RecetaDetalle(
            receta_id=id_receta,
            materia_prima_id=materia_prima_id,
            cantidad_necesaria=cantidad_necesaria,
            unidad_medida=materia.unidad_medida
        )

        try:
            db.session.add(nuevo_detalle)
            db.session.commit()
            flash('Ingrediente agregado correctamente.', 'success')
        except Exception:
            db.session.rollback()
            flash('Ocurrió un error al agregar el ingrediente a la base de datos.', 'danger')

        return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

    return render_template(
        'recetas/ingredientesReceta.html',
        receta=receta,
        materias=materias,
        form=form,
        active_page='recetas.lista_recetas'
    )