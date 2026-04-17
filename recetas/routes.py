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

        # Validaciones de duplicados
        existe_nombre = Receta.query.filter_by(nombre_receta=nombre_limpio).first()
        if existe_nombre:
            form.nombre_receta.errors.append('Esta receta ya existe.')

        existe_producto = Receta.query.filter_by(producto_id=form.producto_id.data).first()
        if existe_producto:
            form.producto_id.errors.append('Ese producto ya tiene una receta registrada.')

        if not form.nombre_receta.errors and not form.producto_id.errors:
            nueva_receta = Receta(
                producto_id=form.producto_id.data,
                nombre_receta=nombre_limpio,
                instrucciones=form.instrucciones.data.strip() if form.instrucciones.data else None
            )

            try:
                db.session.add(nueva_receta)
                db.session.commit()
                flash('Receta agregada correctamente. Ahora agrega sus ingredientes.', 'success')
                return redirect(url_for('recetas.gestionar_ingredientes', id_receta=nueva_receta.id_receta))
            except IntegrityError:
                db.session.rollback()
                form.producto_id.errors.append('Ese producto ya tiene una receta registrada.')
            except Exception as e:
                db.session.rollback()
                print(f"Error al agregar receta: {e}")
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

        # Validar duplicados ignorando la receta actual
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

        if not form.nombre_receta.errors and not form.producto_id.errors:
            receta.producto_id = form.producto_id.data
            receta.nombre_receta = nombre_limpio
            # SE ELIMINÓ receta.cantidad_lote = form.cantidad_lote.data
            receta.instrucciones = form.instrucciones.data.strip() if form.instrucciones.data else None
            receta.activo = bool(int(request.form.get('activo', 1)))

            try:
                db.session.commit()
                flash('Receta actualizada correctamente.', 'success')
                return redirect(url_for('recetas.lista_recetas'))
            except Exception as e:
                db.session.rollback()
                print(f"Error al editar receta: {e}")
                flash('Ocurrió un error al actualizar la receta.', 'danger')

    return render_template(
        'recetas/modificarReceta.html',
        form=form,
        receta=receta,
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
        flash('Error al desactivar.', 'danger')
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
        flash('Error al reactivar.', 'danger')
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
    materias = MateriasPrimas.query.filter_by(activo=True).all()
    form = FlaskForm()

    if request.method == 'POST':
        materia_id = request.form.get('materia_prima_id', type=int)
        cantidad_cap = request.form.get('cantidad_necesaria', type=float) 
        unidad_cap = request.form.get('unidad_receta') 

        materia = MateriasPrimas.query.get_or_404(materia_id)
        cantidad_base = cantidad_cap 
        
        # Lógica de conversión de unidades
        if unidad_cap == 'g' and materia.unidad_medida.lower() == 'kg':
            cantidad_base = cantidad_cap / 1000
        elif unidad_cap == 'mg' and materia.unidad_medida.lower() == 'kg':
            cantidad_base = cantidad_cap / 1000000
        elif unidad_cap == 'ml' and materia.unidad_medida.lower() == 'lt':
            cantidad_base = cantidad_cap / 1000

        nuevo_detalle = RecetaDetalle(
            receta_id=id_receta,
            materia_prima_id=materia_id,
            cantidad_necesaria=cantidad_base,    
            cantidad_capturada=cantidad_cap,     
            unidad_capturada=unidad_cap,        
            unidad_medida=materia.unidad_medida  
        )

        try:
            db.session.add(nuevo_detalle)
            db.session.commit()
            flash('Ingrediente agregado.', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error al agregar ingrediente: {e}")
            flash('Error al guardar ingrediente.', 'danger')

        return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

    return render_template('recetas/ingredientesReceta.html', receta=receta, materias=materias, form=form)

@recetas.route('/recetas/ingrediente/eliminar/<int:id_detalle>', methods=['POST'])
@login_required
def eliminar_ingrediente(id_detalle):
    detalle = RecetaDetalle.query.get_or_404(id_detalle)
    id_receta = detalle.receta_id
    
    try:
        db.session.delete(detalle)
        db.session.commit()
        flash('Ingrediente quitado de la receta.', 'info')
    except Exception:
        db.session.rollback()
        flash('No se pudo quitar el ingrediente.', 'danger')
        
    return redirect(url_for('recetas.gestionar_ingredientes', id_receta=id_receta))

@recetas.route("/recetas/eliminar/confirmar/<int:id_receta>")
@login_required
def confirmar_eliminar_receta(id_receta):
    receta = Receta.query.get_or_404(id_receta)
    form = FlaskForm() # Necesitas esto para el CSRF token

    return render_template(
        "recetas/eliminarReceta.html",
        receta=receta,
        form=form,
        receta_id=id_receta,
        active_page='recetas.lista_recetas'
    )