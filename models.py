from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy.dialects.mysql import LONGTEXT


from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, BooleanField, DateField # Importa DateField
from wtforms.validators import DataRequired, Email, Length, Optional
from flask_wtf.file import FileField, FileAllowed

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    rol = db.Column(db.Enum('ADMIN', 'CLIENTE'), nullable=False, default='CLIENTE')
    activo = db.Column(db.Boolean, default=True)
    
    cliente = db.relationship('Cliente', backref='usuario', uselist=False)



class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), unique=True)
    
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    
    tipo = db.Column(db.Enum('MINORISTA', 
                             'MAYORISTA'), default='MINORISTA')
    fecha_registro = db.Column(db.Date, default=date.today)
    categoria_comprador = db.Column(db.Enum('OCASIONAL', 'FRECUENTE'), default='OCASIONAL')
    
    imagen_cliente = db.Column(LONGTEXT, nullable=True) 
    
    notas = db.Column(db.String(200))
    estatus = db.Column(db.String(10), default='ACTIVO')

    def __repr__(self):
        return f'<Cliente {self.nombre}>'
    
    
class Empleado(db.Model):
    __tablename__ = 'empleados'
    
    id_empleado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    # Cambiado a nullable=True para evitar errores si solo se pone nombre completo en un campo
    apellido = db.Column(db.String(100), nullable=True) 
    dni_cedula = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    puesto = db.Column(db.String(100), nullable=False)
    salario_mensual = db.Column(db.Numeric(10, 2))
    fecha_contratacion = db.Column(db.Date, nullable=True)
    
    # CAMBIO CRÍTICO: Se cambió Text por LONGTEXT para que la imagen no se guarde corrupta
    imagen_empleado = db.Column(LONGTEXT, nullable=True)
    
    estatus = db.Column(db.String(10), default='ACTIVO')

    def __repr__(self):
        return f'<Empleado {self.nombre} - {self.dni_cedula}>'