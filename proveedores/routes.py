from flask import render_template, request, redirect, url_for, flash
from . import proveedores
from . import forms
from models import db, Proveedores
from utils import login_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError


@proveedores.route("/proveedores", methods=["GET", "POST"])
@login_required
def lista_proveedores():
    create_form = forms.ProveedorForm(request.form)

    search_query = request.args.get("q", "").strip()
    query = Proveedores.query

    if search_query:
        filtros = [
            Proveedores.nombre.ilike(f"%{search_query}%"),
            Proveedores.contacto.ilike(f"%{search_query}%"),
        ]
        query = query.filter(or_(*filtros))

    lista_de_proveedores = query.all()

    return render_template(
        "proveedores/proveedoresAdmin.html",
        form=create_form,
        proveedores=lista_de_proveedores,
        search_query=search_query,
    )


# Mostrar detalles de proveedor
@proveedores.route("/proveedores/<int:id>")
@login_required
def detalle_proveedor(id):
    proveedor = Proveedores.query.get_or_404(id)
    return render_template("proveedores/detallesProveedores.html", proveedor=proveedor)


@proveedores.route("/proveedores/agregar", methods=["GET", "POST"])
@login_required
def agregar_proveedor():
    form = forms.ProveedorForm(request.form)

    if request.method == "POST" and form.validate():
        nuevo_prov = Proveedores(
            nombre=form.nombre.data.strip(),
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
            # INICIO DE TRANSACCIÓN ATÓMICA
            db.session.add(nuevo_prov)
            db.session.commit()
            flash("Proveedor registrado exitosamente", "success")
            return redirect(url_for("proveedores.lista_proveedores"))

        except IntegrityError as e:
            db.session.rollback()
            # Detectamos qué campo falló analizando el error de la DB
            error_info = str(e.orig).lower()
            if "ruc" in error_info:
                form.ruc.errors.append("Este RUC ya existe.")
            elif "nombre" in error_info:
                form.nombre.errors.append("Este nombre de empresa ya existe.")
            elif "telefono" in error_info:
                form.telefono.errors.append("Este teléfono ya está registrado.")
            else:
                flash(
                    "Error de duplicidad: Verifique los datos del proveedor.", "danger"
                )

        except Exception as e:
            db.session.rollback()
            flash("Ocurrió un error inesperado.", "danger")

    return render_template("proveedores/agregarProveedores.html", form=form)


# Modificar proveedor
@proveedores.route("/proveedores/modificar/<int:id>", methods=["GET", "POST"])
@login_required
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
@login_required
def eliminar_proveedor(id):
    proveedor = Proveedores.query.get_or_404(id)

    form = forms.ProveedorForm()

    return render_template(
        "proveedores/eliminarProveedores.html", proveedor=proveedor, form=form
    )


@proveedores.route("/proveedores/desactivar/<int:id>", methods=["POST"])
@login_required
def desactivar_proveedor(id):
    proveedor = Proveedores.query.get_or_404(id)
    proveedor.activo = False
    db.session.commit()
    return redirect(url_for("proveedores.lista_proveedores"))
