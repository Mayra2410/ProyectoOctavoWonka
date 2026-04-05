from flask import Flask, render_template
from config import DevelopmentConfig
from models import db
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect  

# Configuración y Modelos (Agrupados)
from config import DevelopmentConfig
from models import db, Usuario 

# Formularios
from forms import LoginForm 
from registro.formsR import ClienteForm

# Blueprints (Los módulos del equipo)
from proveedores.routes import proveedores
from materiaPrima.routes import materia_Prima
from comprasProveedores.routes import compras_bp
from recetas.routes import recetas
from pagosProveedores.routes import pagosProveedores
from puntoVenta.routes import puntoVenta_bp

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Inicialización de extensiones
db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

# Registro de Blueprints
app.register_blueprint(proveedores)
app.register_blueprint(materia_Prima)
app.register_blueprint(compras_bp)


@app.route("/")
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


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
