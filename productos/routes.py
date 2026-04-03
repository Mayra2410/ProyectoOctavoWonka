from flask import render_template, request, redirect, url_for, flash
from . import productos
from .forms import ProductoForm
from models import db, Producto


@productos.route('/productos')
def lista_productos():
    busqueda = request.args.get('q', '').strip()

    query = Producto.query

    if busqueda:
        query = query.filter(Producto.nombre.ilike(f'%{busqueda}%'))

    lista_productos = query.order_by(Producto.id_producto.asc()).all()
    return render_template('productos/productosAdmin.html', productos=lista_productos, busqueda=busqueda)


@productos.route('/productos/agregar', methods=['GET', 'POST'])
def agregar_producto():
    form = ProductoForm()

    if form.validate_on_submit():
        nuevo_producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            categoria=form.categoria.data,
            precio_venta=form.precio_venta.data,
            costo_produccion_estimado=form.costo_produccion_estimado.data,
            unidad_medida=form.unidad_medida.data,
            tiempo_produccion_minutos=form.tiempo_produccion_minutos.data,
            imagen_producto=form.imagen_producto.data,
            activo=form.activo.data
        )

        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado correctamente.', 'success')
        return redirect(url_for('productos.lista_productos'))

    return render_template('productos/agregarProductos.html', form=form)


@productos.route('/productos/editar/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    form = ProductoForm(obj=producto)

    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.categoria = form.categoria.data
        producto.precio_venta = form.precio_venta.data
        producto.costo_produccion_estimado = form.costo_produccion_estimado.data
        producto.unidad_medida = form.unidad_medida.data
        producto.tiempo_produccion_minutos = form.tiempo_produccion_minutos.data
        producto.imagen_producto = form.imagen_producto.data
        producto.activo = form.activo.data

        db.session.commit()
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('productos.lista_productos'))

    return render_template('productos/modificarProductos.html', form=form, producto=producto)


@productos.route('/productos/eliminar/<int:id_producto>', methods=['POST'])
def eliminar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)

    producto.activo = False
    db.session.commit()

    flash('Producto desactivado correctamente.', 'warning')
    return redirect(url_for('productos.lista_productos'))

@productos.route('/productos/reactivar/<int:id_producto>', methods=['POST'])
def reactivar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    producto.activo = True
    db.session.commit()
    flash('Producto reactivado correctamente.', 'success')
    return redirect(url_for('productos.lista_productos'))