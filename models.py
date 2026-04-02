from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class Proveedores(db.Model):
    __tablename__ = "proveedores"

    id_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    ruc = db.Column(db.String(20))
    notas = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.Date, default=datetime.date.today)

    def __repr__(self):
        return f"<Proveedor {self.nombre}>"
