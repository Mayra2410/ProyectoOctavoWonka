from flask import render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from . import productos
from .forms import ProductoForm
from models import db, Producto, Receta
import base64
from utils import login_required


@productos.route("/productos")
@login_required
def lista_productos():
    busqueda = request.args.get("q", "").strip()

    query = Producto.query

    if busqueda:
        query = query.filter(Producto.nombre.ilike(f"%{busqueda}%"))

    lista_productos = query.order_by(Producto.id_producto.asc()).all()

    return render_template(
        "productos/productosAdmin.html",
        productos=lista_productos,
        busqueda=busqueda,
        active_page="productos.lista_productos",
    )


@productos.route("/productos/detalles/<int:id_producto>")
@login_required
def detalle_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    form = ProductoForm(obj=producto)

    return render_template(
        "productos/detallesProductos.html",
        producto=producto,
        form=form,
        active_page="productos.lista_productos",
    )


@productos.route("/productos/agregar", methods=["GET", "POST"])
@login_required
def agregar_producto():
    form = ProductoForm()

    if form.validate_on_submit():
        existe = Producto.query.filter_by(nombre=form.nombre.data).first()
        if existe:
            form.nombre.errors.append("Este producto ya existe.")
            return render_template(
                "productos/agregarProductos.html",
                form=form,
                active_page="productos.lista_productos",
            )

        nuevo_producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            categoria=form.categoria.data,
            precio_venta=form.precio_venta.data,
            costo_produccion_estimado=form.costo_produccion_estimado.data,
            unidad_medida=form.unidad_medida.data,
            tiempo_produccion_minutos=form.tiempo_produccion_minutos.data,
            activo=True,
        )

        file = request.files.get("imagen_producto")
        if file and file.filename != "":
            if not file.content_type or not file.content_type.startswith("image/"):
                flash("El archivo seleccionado no es una imagen válida.", "danger")
                return render_template(
                    "productos/agregarProductos.html",
                    form=form,
                    active_page="productos.lista_productos",
                )

            extensiones_validas = (".jpg", ".jpeg", ".png", ".webp")
            if not file.filename.lower().endswith(extensiones_validas):
                flash("Formato de imagen no permitido.", "danger")
                return render_template(
                    "productos/agregarProductos.html",
                    form=form,
                    active_page="productos.lista_productos",
                )

            try:
                imagen_bytes = file.read()
                encoded = base64.b64encode(imagen_bytes).decode("utf-8")
                nuevo_producto.imagen_producto = (
                    f"data:{file.content_type};base64,{encoded}"
                )
            except Exception as e:
                print(f"Error al procesar imagen del producto: {e}")

        db.session.add(nuevo_producto)
        db.session.commit()
        flash("Producto agregado correctamente.", "success")
        return redirect(url_for("productos.lista_productos"))

    return render_template(
        "productos/agregarProductos.html",
        form=form,
        active_page="productos.lista_productos",
    )


@productos.route("/productos/editar/<int:id_producto>", methods=["GET", "POST"])
@login_required
def editar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    form = ProductoForm(obj=producto)

    if form.validate_on_submit():
        duplicado = Producto.query.filter(
            Producto.nombre == form.nombre.data, Producto.id_producto != id_producto
        ).first()

        if duplicado:
            form.nombre.errors.append("Este nombre de producto ya está registrado.")
            return render_template(
                "productos/modificarProductos.html",
                form=form,
                producto=producto,
                active_page="productos.lista_productos",
            )

        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.categoria = form.categoria.data
        producto.precio_venta = form.precio_venta.data
        producto.costo_produccion_estimado = form.costo_produccion_estimado.data
        producto.unidad_medida = form.unidad_medida.data
        producto.tiempo_produccion_minutos = form.tiempo_produccion_minutos.data
        producto.activo = form.activo.data

        file = request.files.get("imagen_producto")
        if file and file.filename != "":
            if not file.content_type or not file.content_type.startswith("image/"):
                flash("El archivo seleccionado no es una imagen válida.", "danger")
                return render_template(
                    "productos/modificarProductos.html",
                    form=form,
                    producto=producto,
                    active_page="productos.lista_productos",
                )

            extensiones_validas = (".jpg", ".jpeg", ".png", ".webp")
            if not file.filename.lower().endswith(extensiones_validas):
                flash("Formato de imagen no permitido.", "danger")
                return render_template(
                    "productos/modificarProductos.html",
                    form=form,
                    producto=producto,
                    active_page="productos.lista_productos",
                )

            try:
                imagen_bytes = file.read()
                encoded = base64.b64encode(imagen_bytes).decode("utf-8")
                producto.imagen_producto = f"data:{file.content_type};base64,{encoded}"
            except Exception as e:
                print(f"Error al actualizar imagen del producto: {e}")

        db.session.commit()
        flash("Producto actualizado correctamente.", "success")
        return redirect(url_for("productos.lista_productos"))

    return render_template(
        "productos/modificarProductos.html",
        form=form,
        producto=producto,
        active_page="productos.lista_productos",
    )


@productos.route("/productos/eliminar/confirmar/<int:id_producto>")
@login_required
def confirmar_eliminar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    form = FlaskForm()

    return render_template(
        "productos/eliminarProductos.html",
        producto=producto,
        form=form,
        producto_id=id_producto,
        active_page="productos.lista_productos",
    )


@productos.route("/productos/desactivar/<int:id_producto>", methods=["POST"])
@login_required
def desactivar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)

    producto.activo = False

    try:
        db.session.commit()
        flash("Producto desactivado correctamente.", "warning")
        return redirect(url_for("productos.lista_productos"))
    except Exception as e:
        db.session.rollback()
        flash("Ocurrió un error al desactivar el producto.", "danger")
        return redirect(url_for("productos.lista_productos"))


@productos.route("/productos/reactivar/<int:id_producto>", methods=["POST"])
@login_required
def reactivar_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)
    producto.activo = True
    db.session.commit()

    flash("Producto reactivado correctamente.", "success")
    return redirect(url_for("productos.lista_productos"))


@productos.route("/productos/<int:id_producto>/receta")
@login_required
def ver_receta_producto(id_producto):
    producto = Producto.query.get_or_404(id_producto)

    receta = Receta.query.filter_by(producto_id=id_producto).first()

    if not receta:
        flash(
            f'El producto "{producto.nombre}" no tiene una receta registrada.',
            "warning",
        )
        return redirect(url_for("productos.detalle_producto", id_producto=id_producto))

    return render_template(
        "recetas/detalleRecetaProducto.html",
        receta=receta,
        producto=producto,
        active_page="puntoVenta.index",
    )
