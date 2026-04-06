from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash

# Configuración y Modelos
from config import DevelopmentConfig
from models import db, Usuario

# Formularios
from forms import LoginForm 
from registro.formsR import ClienteForm

# --- IMPORTACIÓN DE BLUEPRINTS ---
# Asegúrate de que estas rutas coincidan con tus carpetas
from proveedores.routes import proveedores
from produccion.routes import produccion
from inventario.routes import inventario
from gesVentas.routes import gesVentas
from productos.routes import productos
from materiaPrima.routes import materia_Prima
from comprasProveedores.routes import compras_bp
from recetas.routes import recetas
from pagosProveedores.routes import pagosProveedores
from puntoVenta.routes import puntoVenta_bp
from registro.routesR import registro as registro_blueprint

# IMPORTANTE: Importar el objeto 'cliente' y 'empleado' desde su carpeta
from clientes import cliente
from empleados import empleado

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['SECRET_KEY'] = 'WonkA'

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# --- REGISTRO DE BLUEPRINTS ---
app.register_blueprint(proveedores)
app.register_blueprint(produccion)
app.register_blueprint(inventario)
app.register_blueprint(gesVentas)
app.register_blueprint(productos)
app.register_blueprint(materia_Prima)
app.register_blueprint(compras_bp)
app.register_blueprint(recetas)
app.register_blueprint(pagosProveedores)
app.register_blueprint(puntoVenta_bp, url_prefix='/punto-venta')
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


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)