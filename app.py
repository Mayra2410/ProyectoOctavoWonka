import logging
from flask import Flask, render_template, redirect, url_for, flash, session, request
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, Usuario
from config import DevelopmentConfig

from proveedores.routes import proveedores
from registro.routesR import registro as registro_blueprint
from clientes import cliente
from empleados import empleado
from forms import LoginForm 
from registro.formsR import ClienteForm

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['SECRET_KEY'] = 'WonkA'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('wonka_auditoria.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

db.init_app(app)

app.register_blueprint(proveedores)
app.register_blueprint(registro_blueprint) 
app.register_blueprint(cliente)
app.register_blueprint(empleado)

@app.route("/", methods=["GET", "POST"])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            logging.info(f"Acceso: Usuario {email} inicio sesion correctamente.")
            session['user_id'] = user.id_usuario
            session['rol'] = user.rol
            return redirect(url_for('proveedores.lista_proveedores'))
        else:
            logging.warning(f"Fallo: Intento de conexion erroneo para {email}.")
            flash("Correo o contrasena incorrectos.", "error")
            return redirect(url_for('index'))

    return render_template("index.html", form=form)

@app.route("/recuperar", methods=["GET", "POST"])
def recuperar_password():
    form = ClienteForm()
    del form.imagen_cliente
    del form.nombre
    del form.telefono
    del form.direccion
    del form.tipo

    if form.validate_on_submit():
        email = form.email.data
        nueva_pass = form.password.data
        
        user = Usuario.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(nueva_pass)
            db.session.commit()
            logging.info(f"Auditoria: Contrasena actualizada para {email}")
            flash("Contrasena actualizada con exito.", "success")
            return redirect(url_for('index'))
        else:
            flash("El correo no esta registrado.", "error")
            
    return render_template("recuperarContrasenia/recuperar.html", form=form)


@app.route('/registro', methods=["GET", "POST"])
def registro_pagina():
    form = ClienteForm() 
    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            telefono=form.telefono.data,
            direccion=form.direccion.data,
            rol='Cliente'
        )
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash("Registro exitoso.", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash("Error al registrar.", "error")
            
    return render_template('registro/usuarioRegistro.html', form=form)

@app.route("/logout")
def logout():
    usuario_id = session.get('user_id', 'Anonimo')
    logging.info(f"Salida: El usuario id {usuario_id} cerro sesion.")
    session.clear()
    flash("Has cerrado sesion correctamente.", "info")
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)