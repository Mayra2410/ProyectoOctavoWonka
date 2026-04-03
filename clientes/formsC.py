from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, TextAreaField, DateField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Regexp, Email, Optional

class ClienteForm(FlaskForm):
    nombre = StringField("Nombre Completo", [
        DataRequired(message="El nombre es un campo obligatorio"),
        Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres"),
        Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', message="Este campo solo acepta letras")
    ])

    email = EmailField("Correo Electronico", [
        DataRequired(message="El correo es un campo obligatorio"),
        Email(message="Ingresa un formato de correo valido"),
    ])

    telefono = StringField("Telefono", [
        DataRequired(message="El telefono es un campo obligatorio"),
        Length(min=10, max=20, message="El telefono debe tener entre 10 y 20 digitos"),
        Regexp(r'^[0-9]+$', message="Este campo solo acepta numeros")
    ])

    direccion = StringField("Direccion", [
        DataRequired(message="La direccion es un campo obligatorio"),
        Length(max=200, message="La direccion es demasiado larga"),
    ])

    tipo = SelectField("Tipo de Comprador",
        choices=[('MINORISTA', 'Minorista'), ('MAYORISTA', 'Mayorista')],
        default='MINORISTA'
    )

    categoria_comprador = SelectField("Categoria de Cliente",
        choices=[('OCASIONAL', 'Ocasional'), ('FRECUENTE', 'Frecuente')],
        default='OCASIONAL'
    )

    estatus = SelectField("Estado del Cliente",
        choices=[('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo')],
        default='ACTIVO'
    )

    notas = TextAreaField("Notas Adicionales", [
        Optional(), 
        Length(max=200, message="Maximo 200 caracteres")
    ])
    
    imagen_cliente = FileField("Foto del Cliente", validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo se permiten imagenes (JPG, PNG, JPEG)')
    ])

    fecha_registro = DateField("Fecha de Registro",
        [DataRequired(message="La fecha de registro es un campo obligatorio")],
        format="%Y-%m-%d"
    )