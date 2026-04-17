import base64
import random
import string
from flask import render_template, flash, redirect, url_for, request
from flask_mail import Message
from . import registro
from .formsR import ClienteForm
from models import Usuario, Cliente
from werkzeug.security import generate_password_hash


@registro.route("/registro_cliente", methods=["GET", "POST"])
def registro_cliente():
    from app import db, mail

    form = ClienteForm()

    if form.validate_on_submit():
        try:
            archivo = form.imagen_cliente.data
            contenido_binario = archivo.read()
            encoded_string = base64.b64encode(contenido_binario).decode("utf-8")
            extension = archivo.filename.rsplit(".", 1)[-1].lower()
            base64_image = f"data:image/{extension};base64,{encoded_string}"

            codigo = "".join(random.choices(string.digits, k=6))

            nuevo_usuario = Usuario(
                username=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                email=form.email.data,
                rol="CLIENTE",
                codigo_verificacion=codigo,
                verificado=False,
            )
            db.session.add(nuevo_usuario)
            db.session.flush()

            nuevo_cliente = Cliente(
                usuario_id=nuevo_usuario.id_usuario,
                nombre=form.nombre.data,
                email=form.email.data,
                telefono=form.telefono.data,
                direccion=form.direccion.data,
                imagen_cliente=base64_image,
            )
            db.session.add(nuevo_cliente)
            db.session.commit()

            try:
                msg = Message("Tu Código Dorado Wonka", recipients=[form.email.data])
                msg.body = f"¡Hola! Tu código de acceso es: {codigo}"
                mail.send(msg)
            except Exception as e:
                print(f"Error de envío: {e}")
                flash(
                    "Usuario creado, pero hubo un error enviando el correo. Contacta soporte.",
                    "warning",
                )

            return redirect(url_for("registro.verificar_codigo", email=form.email.data))

        except Exception as e:
            db.session.rollback()
            flash(f"Error crítico en el registro: {str(e)}", "error")

    return render_template("registro/usuarioRegistro.html", form=form)


@registro.route("/verificar_codigo/<email>", methods=["GET", "POST"])
def verificar_codigo(email):
    from app import db

    if request.method == "POST":
        codigo_ingresado = request.form.get("codigo").strip()
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and str(usuario.codigo_verificacion) == str(codigo_ingresado):
            usuario.verificado = True
            usuario.codigo_verificacion = None
            db.session.commit()

            from .formsR import ClienteForm

            return render_template(
                "registro/usuarioRegistro.html",
                registro_exitoso=True,
                form=ClienteForm(formdata=None),
            )
        else:
            flash("Código incorrecto. Inténtalo de nuevo.", "error")

    return render_template("registro/verificar_codigo.html", email=email)
