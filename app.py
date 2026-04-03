from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from models import db, Usuario
from config import DevelopmentConfig
from proveedores.routes import proveedores
from registro.routesR import registro as registro_blueprint
from registro.formsR import ClienteForm
from clientes import cliente
from empleados import empleado
from forms import LoginForm 

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['SECRET_KEY'] = 'WonkA'

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
            session['user_id'] = user.id_usuario
            session['rol'] = user.rol
            return redirect(url_for('proveedores.lista_proveedores'))
        else:
            flash("Correo o contraseña incorrectos. Intenta de nuevo.", "error")
            return redirect(url_for('index'))

    return render_template("index.html", form=form)

@app.route('/registro')
def registro_pagina():
    form = ClienteForm()
    return render_template('registro/usuarioRegistro.html', form=form)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)