from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from config import DevelopmentConfig
from models import db, Usuario
from forms import LoginForm
from datetime import datetime, timedelta
from flask_mail import Mail, Message
import logging
import random
import base64
import os

from proveedores.routes import proveedores
from registro.routesR import registro as registro_blueprint
from clientes import cliente
from empleados import empleado
from recuperarContrasenia import recuperarContrasenia

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config["SECRET_KEY"] = "WonKA"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'pruebawonka1@gmail.com'
app.config['MAIL_PASSWORD'] = 'ankapkaclgspdhfm'
app.config['MAIL_DEFAULT_SENDER'] = ('Wonka', 'tu_correo@gmail.com')

mail = Mail(app)
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler("wonka_auditoria.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logging.getLogger().addHandler(file_handler)

app.register_blueprint(proveedores)
app.register_blueprint(registro_blueprint)
app.register_blueprint(cliente)
app.register_blueprint(empleado)
app.register_blueprint(recuperarContrasenia)

@app.route("/", methods=["GET", "POST"])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Usuario.query.filter_by(email=email).first()

        if user:
            if hasattr(user, 'verificado') and not user.verificado:
                flash("Tu cuenta aún no está verificada...", "warning")
                return redirect(url_for('registro.verificar_codigo', email=user.email))

            if user.bloqueado_hasta and user.bloqueado_hasta > datetime.now():
                minutos_restantes = int((user.bloqueado_hasta - datetime.now()).total_seconds() / 60)
                flash(f"Cuenta bloqueada temporalmente. Intenta en {minutos_restantes + 1} min.", "danger")
                return redirect(url_for('index'))

            if check_password_hash(user.password_hash, password):
                user.intentos_fallidos = 0
                user.bloqueado_hasta = None
                db.session.commit()

                session['user_id'] = user.id_usuario
                session['rol'] = user.rol
                session['nombre'] = user.username
                return redirect(url_for('cliente.clientesAdmin'))
            
            else:
                user.intentos_fallidos += 1
                if user.intentos_fallidos >= 3:
                    user.bloqueado_hasta = datetime.now() + timedelta(minutes=10)
                    logging.warning(f"Auditoria: Cuenta bloqueada: {email}")
                    flash("Cuenta bloqueada por 10 minutos por exceso de intentos.", "danger")
                else:
                    intentos_quedan = 3 - user.intentos_fallidos
                    flash(f"Contraseña incorrecta. Quedan {intentos_quedan} intentos.", "danger")
                
                db.session.commit()
                return redirect(url_for('index'))
        else:
            flash("Correo o contraseña incorrectos.", "danger")
            return redirect(url_for('index'))

    return render_template("index.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("index"))

@app.route('/catalogo')
def catalogo():
    db.session.remove() 
    result = db.session.execute(db.text("SELECT * FROM productos WHERE activo = 1"))
    productos_db = [dict(row._mapping) for row in result]
    return render_template('vistaCatalogo/catalogo.html', productos=productos_db)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)