from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, FileField, PasswordField
from flask_wtf.file import FileAllowed 
from wtforms.validators import Regexp, DataRequired, Length, Email, ValidationError
from models import Cliente

class ClienteForm(FlaskForm):
    nombre = StringField("Nombre Completo", [
        DataRequired(message="El campo nombre es obligatorio"),
        Length(min=4, max=100, message="El nombre debe tener entre 4 y 100 caracteres"),
        Regexp(r'^[a-zA-Z\s]+$', message="Este campo solo acepta letras")
    ])
    
    email = EmailField("Correo Electronico", [
        DataRequired(message="El correo es obligatorio"),
        Email(message="Ingresa un correo valido")
    ])
    def validate_email(self, email):
        cliente_existente = Cliente.query.filter_by(email=email.data).first()
        if cliente_existente:
            raise ValidationError("Este correo ya esta registrado")
    
    telefono = StringField("Telefono", [
        DataRequired(message="El numero de telefono es obligatorio"),
        Length(min=10, max=10, message="Deben ser 10 digitos"),
        Regexp(r'^[0-9]+$', message="Este campo solo acepta numeros")
    ])
    
    direccion = StringField("Direccion", [
        DataRequired(message="La direccion es obligatoria")
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