from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from . import recetas
from .forms import RecetaForm
from models import db, Receta, Producto, MateriasPrimas, RecetaDetalle


@recetas.route('/recetas')
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
def agregar_receta():
    form = RecetaForm()
    form.producto_id.choices = [(p.id_producto, p.nombre) for p in Producto.query.all()]

    if form.validate_on_submit():
        existe = Receta.query.filter_by(nombre_receta=form.nombre_receta.data).first()
        if existe:
            form.nombre_receta.errors.append('Esta receta ya existe.')
            return render_template(
                'recetas/agregarReceta.html',
                form=form,
                active_page='recetas.lista_recetas'
            )

        nueva_receta = Receta(
            producto_id=form.producto_id.data,
            nombre_receta=form.nombre_receta.data,
            cantidad_lote=form.cantidad_lote.data,
            instrucciones=form.instrucciones.data,
            activo = bool(int(request.form.get('activo', 1)))
        )

        db.session.add(nueva_receta)
        db.session.commit()
        flash('Receta agregada correctamente. Ahora agrega sus ingredientes.', 'success')
        return redirect(url_for('recetas.gestionar_ingredientes', id_receta=nueva_receta.id_receta))

    return render_template(
        'recetas/agregarReceta.html',
        form=form,
        active_page='recetas.lista_recetas'
    )


@recetas.route('/recetas/editar/<int:id_receta>', methods=['GET', 'POST'])
def modificar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    form = RecetaForm(obj=receta)
    form.producto_id.choices = [(p.id_producto, p.nombre) for p in Producto.query.all()]

    if form.validate_on_submit():
        duplicado = Receta.query.filter(
            Receta.nombre_receta == form.nombre_receta.data,
            Receta.id_receta != id_receta
        ).first()

        if duplicado:
            form.nombre_receta.errors.append('Este nombre de receta ya está registrado.')
            return render_template(
                'recetas/modificarReceta.html',
                form=form,
                receta=receta,
                active_page='recetas.lista_recetas'
            )

        receta.producto_id = form.producto_id.data
        receta.nombre_receta = form.nombre_receta.data
        receta.cantidad_lote = form.cantidad_lote.data
        receta.instrucciones = form.instrucciones.data
        receta.activo = bool(int(request.form.get('activo', 1)))

        db.session.commit()
        flash('Receta actualizada correctamente.', 'success')
        return redirect(url_for('recetas.lista_recetas'))

    return render_template(
        'recetas/modificarReceta.html',
        form=form,
        receta=receta,
        active_page='recetas.lista_recetas'
    )


@recetas.route("/recetas/eliminar/confirmar/<int:id_receta>")
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
def desactivar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)

    receta.activo = False

    try:
        db.session.commit()
        flash('Receta desactivada correctamente.', 'warning')
        return redirect(url_for("recetas.lista_recetas"))
    except Exception:
        db.session.rollback()
        flash('Ocurrió un error al desactivar la receta.', 'danger')
        return redirect(url_for("recetas.lista_recetas"))


@recetas.route('/recetas/reactivar/<int:id_receta>', methods=['POST'])
def reactivar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    receta.activo = True
    db.session.commit()

    flash('Receta reactivada correctamente.', 'success')
    return redirect(url_for('recetas.lista_recetas'))



@recetas.route('/recetas/detalles/<int:id_receta>')
def detalle_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)

    return render_template(
        'recetas/detallesRecetas.html',
        receta=receta,
        active_page='recetas.lista_recetas'
    )

@recetas.route('/recetas/<int:id_receta>/ingredientes', methods=['GET', 'POST'])
def gestionar_ingredientes(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    materias = MateriasPrimas.query.filter_by(activo=True).order_by(MateriasPrimas.nombre.asc()).all()
    form = FlaskForm()

    if request.method == 'POST':
        materia_prima_id = request.form.get('materia_prima_id', type=int)
        cantidad_necesaria = request.form.get('cantidad_necesaria', type=float)

        if not materia_prima_id or cantidad_necesaria is None:
            flash('Selecciona la materia prima y escribe la cantidad necesaria.', 'warning')
            return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

        materia = MateriasPrimas.query.get_or_404(materia_prima_id)

        existente = RecetaDetalle.query.filter_by(
            receta_id=id_receta,
            materia_prima_id=materia_prima_id
        ).first()

        if existente:
            flash('Esa materia prima ya está agregada a la receta.', 'warning')
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
            flash('Ocurrió un error al agregar el ingrediente.', 'danger')

        return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

    return render_template(
        'recetas/ingredientesReceta.html',
        receta=receta,
        materias=materias,
        form=form,
        active_page='recetas.lista_recetas'
    )