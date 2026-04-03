from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date  # Importamos ambas clases directamente

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

    fecha_registro = db.Column(db.Date, default=date.today)

    materias = db.relationship("MateriasPrimas", backref="proveedor", lazy=True)

    def __repr__(self):
        return f"<Proveedor {self.nombre}>"


class MateriasPrimas(db.Model):
    __tablename__ = "materias_primas"

    id_materia_prima = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    unidad_medida = db.Column(db.String(20), nullable=False)
    stock_actual = db.Column(db.Numeric(10, 2), default=0.0)
    stock_minimo = db.Column(db.Numeric(10, 2), default=10.0)
    costo_unitario = db.Column(db.Numeric(10, 2))
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id_proveedor"))
    fecha_ultima_compra = db.Column(db.Date)
    porcentaje_merma = db.Column(db.Numeric(5, 2), default=0.0)
    imagen_materia = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<MateriaPrima {self.nombre}>"


class ComprasMateriaPrima(db.Model):
    __tablename__ = "compras_materia_prima"

    id_compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    materia_prima_id = db.Column(
        db.Integer, db.ForeignKey("materias_primas.id_materia_prima"), nullable=False
    )
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id_proveedor"))
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    fecha_compra = db.Column(db.DateTime, default=datetime.now)

    observaciones = db.Column(db.String(200))

    materia_prima = db.relationship("MateriasPrimas", backref="historial_compras")
    proveedor_rel = db.relationship("Proveedores", backref="compras_realizadas")

    def __repr__(self):
        return f"<Compra ID: {self.id_compra}>"
