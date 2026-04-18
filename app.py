import logging
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message

# Configuración local
from config import DevelopmentConfig
from models import db, Usuario
from forms import LoginForm
from registro.formsR import ClienteForm

# --- IMPORTACIÓN DE TODOS LOS BLUEPRINTS ---
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
from clientes import cliente
from empleados import empleado
from recuperarContrasenia import recuperarContrasenia  # Tu blueprint de recuperación

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config["SECRET_KEY"] = "WonKA"

# --- CONFIGURACIÓN DE MAIL (Smtp Gmail) ---
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "pruebawonka1@gmail.com"
app.config["MAIL_PASSWORD"] = "ankapkaclgspdhfm"
app.config["MAIL_DEFAULT_SENDER"] = ("Wonka", "pruebawonka1@gmail.com")

# Inicialización de extensiones
mail = Mail(app)
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# --- CONFIGURACIÓN DE LOGGING / AUDITORÍA ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
file_handler = logging.FileHandler("wonka_auditoria.log", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logging.getLogger().addHandler(file_handler)

# --- REGISTRO DE TODOS LOS BLUEPRINTS ---
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
app.register_blueprint(recuperarContrasenia)  # Registrado para evitar BuildError

# --- RUTAS PRINCIPALES ---


@app.route("/", methods=["GET", "POST"])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Usuario.query.filter_by(email=email).first()

        if user:
            # 1. Verificar si la cuenta está verificada (Lógica de ella)
            if hasattr(user, "verificado") and not user.verificado:
                flash("Tu cuenta aún no está verificada...", "warning")
                return redirect(url_for("registro.verificar_codigo", email=user.email))

            # 2. Verificar bloqueo por intentos (Lógica de ambos)
            if user.bloqueado_hasta and user.bloqueado_hasta > datetime.now():
                minutos_restantes = int(
                    (user.bloqueado_hasta - datetime.now()).total_seconds() / 60
                )
                flash(
                    f"Cuenta bloqueada. Intenta en {minutos_restantes + 1} min.",
                    "danger",
                )
                return redirect(url_for("index"))

            # 3. Validar contraseña
            if check_password_hash(user.password_hash, password):
                user.intentos_fallidos = 0
                user.bloqueado_hasta = None
                db.session.commit()

                session["user_id"] = user.id_usuario
                session["rol"] = user.rol
                session["nombre"] = user.username

                # Redirección inteligente según rol
                if user.rol == "CLIENTE":
                    return redirect(url_for("puntoVenta.index"))
                else:
                    return redirect(url_for("proveedores.lista_proveedores"))

            else:
                # Fallo de contraseña: aumentar contador
                user.intentos_fallidos += 1
                if user.intentos_fallidos >= 3:
                    user.bloqueado_hasta = datetime.now() + timedelta(minutes=10)
                    logging.warning(
                        f"Auditoria: Cuenta bloqueada por intentos: {email}"
                    )
                    flash(
                        "Has superado los intentos permitidos. Bloqueada por 10 min.",
                        "danger",
                    )
                else:
                    intentos_quedan = 3 - user.intentos_fallidos
                    flash(
                        f"Contraseña incorrecta. Te quedan {intentos_quedan} intentos.",
                        "danger",
                    )

                db.session.commit()
                return redirect(url_for("index"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")
            return redirect(url_for("index"))

    return render_template("index.html", form=form)


@app.route("/logout")
def logout():
    usuario_id = session.get("user_id", "Anonimo")
    logging.info(f"Salida: Usuario {usuario_id} cerró sesión.")
    session.clear()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("index"))


@app.route("/catalogo")
def catalogo():
    # Consulta limpia usando SQLAlchemy para el catálogo
    result = db.session.execute(db.text("SELECT * FROM productos WHERE activo = 1"))
    productos_db = [dict(row._mapping) for row in result]
    return render_template("vistaCatalogo/catalogo.html", productos=productos_db)


@app.after_request
def add_header(response):
    """
    Indica al navegador que no guarde copia de las páginas en el caché.
    Esto obliga a validar el login cada que se presiona el botón de 'atrás'.
    """
    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "-1"
    return response


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
