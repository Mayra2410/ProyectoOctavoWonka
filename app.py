from flask import Flask, render_template
from config import DevelopmentConfig 
from models import db
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Tus Blueprints
from proveedores.routes import proveedores
from produccion.routes import produccion
from inventario.routes import inventario
from gesVentas.routes import gesVentas

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)

db.init_app(app)
migrate = Migrate(app, db)
app.register_blueprint(proveedores)
app.register_blueprint(produccion)
app.register_blueprint(inventario)
app.register_blueprint(gesVentas)

@app.route("/")
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)