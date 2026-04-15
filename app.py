from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from config import DevelopmentConfig
from models import db, Usuario

from forms import LoginForm
from registro.formsR import ClienteForm
from datetime import datetime, timedelta
# --- IMPORTACIÓN DE BLUEPRINTS ---
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
import logging

from clientes import cliente
from empleados import empleado

#from pymongo import MongoClient
#from flask import current_app


#def get_mongo_db():
  #  client = MongoClient(current_app.config["MONGO_URI"])
   # return client[current_app.config["MONGO_DB"]]


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config["SECRET_KEY"] = "WonkA"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
file_handler = logging.FileHandler("wonka_auditoria.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logging.getLogger().addHandler(file_handler)

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
app.register_blueprint(puntoVenta_bp, url_prefix="/punto-venta")
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

        if user:
            # 1. Verificar si la cuenta está bloqueada temporalmente
            if user.bloqueado_hasta and user.bloqueado_hasta > datetime.now():
                minutos_restantes = int((user.bloqueado_hasta - datetime.now()).total_seconds() / 60)
                flash(f"Cuenta bloqueada temporalmente. Intenta de nuevo en {minutos_restantes + 1} minutos.", "danger")
                return redirect(url_for('index'))

            # 2. Validar contraseña
            if check_password_hash(user.password_hash, password):
                # Éxito: Reiniciar contador y desbloquear
                user.intentos_fallidos = 0
                user.bloqueado_hasta = None
                db.session.commit()

                session['user_id'] = user.id_usuario
                session['rol'] = user.rol
                session['nombre'] = user.username
                
                return redirect(url_for('puntoVenta.index') if user.rol == 'CLIENTE' else url_for('proveedores.lista_proveedores'))
            
            else:
                # 3. Contraseña incorrecta: Aumentar intentos
                user.intentos_fallidos += 1
                
                if user.intentos_fallidos >= 3:
                    # Aplicar bloqueo por 10 minutos
                    user.bloqueado_hasta = datetime.now() + timedelta(minutes=10)
                    logging.warning(f"Auditoria: Cuenta bloqueada por intentos fallidos: {email}")
                    flash("Has superado el número de intentos. Tu cuenta ha sido bloqueada por 10 minutos.", "danger")
                else:
                    intentos_quedan = 3 - user.intentos_fallidos
                    flash(f"Contraseña incorrecta. Te quedan {intentos_quedan} intentos antes de bloquear la cuenta.", "danger")
                
                db.session.commit()
                return redirect(url_for('index'))
        else:
            # Por seguridad, no decimos si el correo existe o no
            flash("Correo o contraseña incorrectos.", "danger")
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
            return redirect(url_for("index"))
        else:
            flash("El correo no esta registrado.", "error")

    return render_template("recuperarContrasenia/recuperar.html", form=form)


@app.route("/registro", methods=["GET", "POST"])
def registro_pagina():
    form = ClienteForm()
    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            telefono=form.telefono.data,
            direccion=form.direccion.data,
            rol="Cliente",
        )
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash("Registro exitoso.", "success")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            flash("Error al registrar.", "error")

    return render_template("registro/usuarioRegistro.html", form=form)


@app.route("/logout")
def logout():
    usuario_id = session.get("user_id", "Anonimo")
    logging.info(f"Salida: El usuario id {usuario_id} cerro sesion.")
    session.clear()
    flash("Has cerrado sesion correctamente.", "info")
    return redirect(url_for("index"))

@app.route('/catalogo')
def catalogo():
    items_db = db.session.execute(db.text("SELECT * FROM productos")).fetchall()
    
    return render_template('vistaCatalogo/catalogo.html', productos=items_db)




if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
