from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, FileField, PasswordField
from wtforms import validators
from flask_wtf.file import FileAllowed 
from wtforms.validators import Regexp, DataRequired, Length, Email

class ClienteForm(FlaskForm):
    nombre = StringField("Nombre Completo", [
        DataRequired(message="El campo nombre es obligatorio"),
        Length(min=4, max=100),
        Regexp(r'^[a-zA-Z\s]+$', message="Este campo solo acepta letras")
    ])
    
    email = EmailField("Correo Electronico", [
        DataRequired(message="El correo es obligatorio"),
        Email(message="Ingresa un correo valido")
    ])
    
    telefono = StringField("Telefono", [
        DataRequired(message="El numero de telefono es obligatorio"),
        Length(min=10, max=10, message="Deben ser 10 digitos"),
        Regexp(r'^[0-9]+$', message="Solo numeros")
    ])
    
    direccion = StringField("Direccion", [
        DataRequired(message="La direccion es necesaria")
    ])
    
    tipo = SelectField("Tipo de Comprador", choices=[
        ('MINORISTA', 'Minorista'),
        ('MAYORISTA', 'Mayorista')
    ])

    password = PasswordField("Contrasena", [
        DataRequired(message="La contrasena es obligatoria"),
        Length(min=8, message="Minimo 8 caracteres"),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.])[A-Za-z\d@$!%*?&.]{8,}$',
               message="Debe incluir mayuscula, minuscula, numero y simbolo (@$!%*?&.)")
    ])
    
    imagen_cliente = FileField("Foto del Cliente", validators=[
        DataRequired(message="La fotografia es obligatoria"),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imagenes JPG o PNG')
    ])