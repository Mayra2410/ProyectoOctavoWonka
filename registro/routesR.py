import logging
import base64
from flask import render_template, flash, redirect, url_for
from . import registro
from .formsR import ClienteForm
from models import db, Usuario, Cliente
from werkzeug.security import generate_password_hash
from utils import login_required


@registro.route("/registro_cliente", methods=["GET", "POST"])
def registro_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        try:
            logging.info(f"INTENTO DE REGISTRO: {form.email.data}")

            archivo = form.imagen_cliente.data
            contenido_binario = archivo.read()
            encoded_string = base64.b64encode(contenido_binario).decode("utf-8")
            extension = archivo.filename.rsplit(".", 1)[-1].lower()
            base64_image = f"data:image/{extension};base64,{encoded_string}"

            nuevo_usuario = Usuario(
                username=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                email=form.email.data,
                rol="CLIENTE",
            )
            db.session.add(nuevo_usuario)
            db.session.flush()

            nuevo_cliente = Cliente(
                usuario_id=nuevo_usuario.id_usuario,
                nombre=form.nombre.data,
                email=form.email.data,
                telefono=form.telefono.data,
                direccion=form.direccion.data,
                tipo=form.tipo.data,
                imagen_cliente=base64_image,
            )

            db.session.add(nuevo_cliente)
            db.session.commit()

            logging.info(f"REGISTRO EXITOSO: Cliente {form.email.data} creado.")

            return render_template(
                "registro/usuarioRegistro.html",
                form=ClienteForm(formdata=None),
                registro_exitoso=True,
            )

        except Exception as e:
            db.session.rollback()
            logging.error(f"FALLO EN REGISTRO: {str(e)}")
            flash(f"Error en el sistema: {str(e)}", "error")

    return render_template("registro/usuarioRegistro.html", form=form)
