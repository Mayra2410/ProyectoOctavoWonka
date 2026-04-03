from flask import Flask, render_template
from config import DevelopmentConfig
from models import db
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from proveedores.routes import proveedores
from productos.routes import productos
from materiaPrima.routes import materia_Prima
from comprasProveedores.routes import compras_bp


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db.init_app(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)

app.register_blueprint(proveedores)
app.register_blueprint(productos)
app.register_blueprint(materia_Prima)
app.register_blueprint(compras_bp)



@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)
