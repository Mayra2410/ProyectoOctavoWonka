from flask import render_template, request, redirect, url_for
from . import proveedores
from . import forms
from models import db, Proveedores


# Mostrar lista de proveedores en la tabla
@proveedores.route("/proveedores", methods=["GET", "POST"])
def lista_proveedores():
    create_form = forms.ProveedorForm(request.form)
    lista_de_proveedores = Proveedores.query.all()

    return render_template(
        "proveedores/proveedoresAdmin.html",
        form=create_form,
        proveedores=lista_de_proveedores,
    )


# Mostrar detalles de proveedor
@proveedores.route("/proveedores/<int:id>")
def detalle_proveedor(id):
    proveedor = Proveedores.query.get_or_404(id)
    return render_template("proveedores/detallesProveedores.html", proveedor=proveedor)


# Agregar nuevo proveedor
@proveedores.route("/proveedores/agregar", methods=["GET", "POST"])
def agregar_proveedor():
    form = forms.ProveedorForm(request.form)

    if request.method == "POST" and form.validate():
        existe_ruc = Proveedores.query.filter_by(ruc=form.ruc.data).first()
        existe_nombre = Proveedores.query.filter_by(nombre=form.nombre.data).first()
        existe_tel = Proveedores.query.filter_by(telefono=form.telefono.data).first()
        existe_dir = Proveedores.query.filter_by(direccion=form.direccion.data).first()

        if existe_ruc:
            form.ruc.errors.append("Este RUC ya está registrado.")
        if existe_nombre:
            form.nombre.errors.append("Ya existe una empresa con este nombre.")
        if existe_tel:
            form.telefono.errors.append("Este teléfono ya pertenece a otro proveedor.")
        if existe_dir:
            form.direccion.errors.append("Esta dirección ya está registrada.")

        if existe_ruc or existe_nombre or existe_tel or existe_dir:
            return render_template("proveedores/agregarProveedores.html", form=form)

        nuevo_prov = Proveedores(
            nombre=form.nombre.data,
            contacto=form.contacto.data,
            email=form.email.data,
            telefono=form.telefono.data,
            ruc=form.ruc.data,
            direccion=form.direccion.data,
            notas=form.notas.data,
            activo=bool(form.activo.data),
            fecha_registro=form.fecha_registro.data,
        )

        try:
            db.session.add(nuevo_prov)
            db.session.commit()
            return redirect(url_for("proveedores.lista_proveedores"))
        except Exception as e:
            db.session.rollback()

    return render_template("proveedores/agregarProveedores.html", form=form)


# Modificar proveedor
@proveedores.route("/proveedores/modificar/<int:id>", methods=["GET", "POST"])
def modificar_proveedor(id):
    proveedor = Proveedores.query.get_or_404(id)
    form = forms.ProveedorForm(request.form, obj=proveedor)

    if request.method == "POST" and form.validate():

        duplicado_ruc = Proveedores.query.filter(
            Proveedores.ruc == form.ruc.data, Proveedores.id_proveedor != id
        ).first()

        duplicado_nombre = Proveedores.query.filter(
            Proveedores.nombre == form.nombre.data, Proveedores.id_proveedor != id
        ).first()

        duplicado_tel = Proveedores.query.filter(
            Proveedores.telefono == form.telefono.data, Proveedores.id_proveedor != id
        ).first()

        duplicado_dir = Proveedores.query.filter(
            Proveedores.direccion == form.direccion.data, Proveedores.id_proveedor != id
        ).first()

        if duplicado_ruc:
            form.ruc.errors.append("Este RUC pertenece a otro proveedor.")
        if duplicado_nombre:
            form.nombre.errors.append("Ese nombre ya lo usa otra empresa.")
        if duplicado_tel:
            form.telefono.errors.append("Este teléfono ya lo tiene otro proveedor.")
        if duplicado_dir:
            form.direccion.errors.append(
                "Esta dirección ya está registrada en otro proveedor."
            )

        if duplicado_ruc or duplicado_nombre or duplicado_tel or duplicado_dir:
            return render_template(
                "proveedores/modificarProveedores.html", form=form, proveedor_id=id
            )

        form.populate_obj(proveedor)
        proveedor.activo = bool(form.activo.data)

        try:
            db.session.commit()
            return redirect(url_for("proveedores.lista_proveedores"))
        except Exception as e:
            db.session.rollback()

    return render_template(
        "proveedores/modificarProveedores.html", form=form, proveedor_id=id
    )


# Eliminar un proveedor (cambia a inactivo)
@proveedores.route("/proveedores/eliminar/confirmar/<int:id>")
def eliminar_proveedor(id):
    proveedor = Proveedores.query.get_or_404(id)

    form = forms.ProveedorForm()

    return render_template(
        "proveedores/eliminarProveedores.html", proveedor=proveedor, form=form
    )


@proveedores.route("/proveedores/desactivar/<int:id>", methods=["POST"])
def desactivar_proveedor(id):
    proveedor = Proveedores.query.get_or_404(id)
    proveedor.activo = False
    db.session.commit()
    return redirect(url_for("proveedores.lista_proveedores"))
