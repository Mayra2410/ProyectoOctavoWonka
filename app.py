import logging
from flask import Flask, render_template, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
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

logging.basicConfig(
    filename='wonka_auditoria.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

db.init_app(app)

app.register_blueprint(proveedores)
app.register_blueprint(registro_blueprint, url_prefix='/registro') 
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
            logging.info(f"ACCESO: Usuario {email} inicio sesion correctamente.")
            
            session['user_id'] = user.id_usuario
            session['rol'] = user.rol
            return redirect(url_for('proveedores.lista_proveedores'))
        else:
            logging.warning(f"FALLO: Intento de conexion erroneo para {email}.")
            flash("Correo o contrasena incorrectos.", "error")
            return redirect(url_for('index'))

    return render_template("index.html", form=form)

@app.route('/registro')
def registro_pagina():
    form = ClienteForm() 
    return render_template('registro/usuarioRegistro.html', form=form)

@app.route("/logout")
def logout():
    usuario_id = session.get('user_id', 'Anonimo')
    logging.info(f"SALIDA: El usuario ID {usuario_id} cerro sesion.")
    session.clear()
    flash("Has cerrado sesion correctamente.", "info")
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)