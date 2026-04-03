import base64
from flask import render_template, flash
from . import registro
from .formsR import ClienteForm
from models import db, Usuario, Cliente
from werkzeug.security import generate_password_hash

@registro.route('/registro_cliente', methods=['GET', 'POST'])
def registro_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        archivo = form.imagen_cliente.data
        base64_image = None

        if archivo:
            contenido_binario = archivo.read()
            encoded_string = base64.b64encode(contenido_binario).decode('utf-8')
            extension = archivo.filename.rsplit('.', 1)[-1].lower()
            base64_image = f"data:image/{extension};base64,{encoded_string}"

        try:
            nuevo_usuario = Usuario(
                username=form.email.data,
                password_hash=generate_password_hash(form.password.data), 
                email=form.email.data,
                rol='CLIENTE'
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
                imagen_cliente=base64_image
            )
            
            db.session.add(nuevo_cliente)
            db.session.commit()
            
            return render_template('registro/usuarioRegistro.html', 
                                 form=ClienteForm(formdata=None), 
                                 registro_exitoso=True)

        except Exception as e:
            db.session.rollback()
            flash(f"Error en BD: {str(e)}", "error")

    return render_template('registro/usuarioRegistro.html', form=form)