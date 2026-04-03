from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, FileField, PasswordField
from wtforms import validators
from flask_wtf.file import FileAllowed 
from wtforms.validators import Regexp

class ClienteForm(FlaskForm):
    nombre = StringField("Nombre Completo", [
        validators.DataRequired(message="El campo nombre es obligatorio"),
        validators.Length(min=4, max=100),
        Regexp(r'^[a-zA-Z\s]+$', 
               message="Este campo solo acepta letras")
    ])
    
    email = EmailField("Correo Electronico", [
        validators.DataRequired(message="El correo es obligatorio"),
        validators.Email(message="Ingresa un correo valido")
    ])
    
    telefono = StringField("Telefono", [
        validators.DataRequired(message="El numero de telefono es obligatorio"),
        validators.Length(min=7, max=10),
        Regexp(r'^[0-9]+$', 
               message="Este campo solo acepta números")
    ])
    
    direccion = StringField("Direccion", [
        validators.DataRequired(message="La direccion es necesaria")
    ])
    
    tipo = SelectField("Tipo de Comprador", choices=[
        ('MINORISTA', 'Minorista'),
        ('MAYORISTA', 'Mayorista')
    ])
    password = PasswordField("Contraseña", [
        validators.DataRequired(message="La contraseña es obligatoria"),
        validators.Length(min=6, message="La contraseña debe tener al menos 6 caracteres")
    ])
    
    imagen_cliente = FileField("Foto del Cliente", validators=[
        validators.DataRequired(message="La fotografia debe ser obligatoria"),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imagenes JPG o PNG')
    ])
    
    