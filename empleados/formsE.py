from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, DecimalField, DateField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, Optional, Regexp, NumberRange
from wtforms.widgets import TextInput

class EmpleadoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[
        DataRequired(message="El nombre es un campo obligatorio"),
        Length(min=3, message="El nombre debe tener al menos 3 caracteres"),
        Regexp(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', message="Este campo solo acepta letras")
    ])
    apellido = StringField("Apellidos", validators=[Optional()])
    dni_cedula = StringField("DNI/RFC", validators=[
        DataRequired(message="La identificacion es un campo obligatorio")
    ])
    email = EmailField("Correo", validators=[
        DataRequired(message="El correo es un campo obligatorio"),
        Email(message="Ingrese un correo valido")
    ])
    telefono = StringField("Telefono", validators=[
        DataRequired(message="El telefono es un campo obligatorio"),
        Regexp(r'^[0-9]+$', message="Este campo solo acepta numeros")
    ])
    puesto = SelectField("Puesto", choices=[
        ('GERENTE', 'Gerente'),
        ('CHOCOLATERO', 'Chocolatero'),
        ('VENTAS', 'Ventas')
    ], validators=[DataRequired(message="Seleccione un puesto")])
    
    salario_mensual = DecimalField("Salario", places=2, default=0.00, validators=[
        DataRequired(message="El salario es obligatorio"),
        NumberRange(min=0, message="El salario no puede ser un numero negativo")
    ])
    
    fecha_contratacion = DateField("Fecha de Contratacion", 
        format='%Y-%m-%d',
        widget=TextInput(), 
        validators=[DataRequired(message="La fecha es un campo obligatorio")],
        render_kw={"placeholder": "Seleccionar fecha...", "class": "wonka-date"}
    )
    
    imagen_empleado = FileField("Foto", validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imagenes')
    ])
    direccion = StringField("Direccion", validators=[Optional()])