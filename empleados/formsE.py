from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    SelectField,
    DecimalField,
    DateField,
    PasswordField,
)
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Optional,
    Regexp,
    NumberRange,
)


class EmpleadoForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=3, message="Minimo 3 caracteres"),
            Regexp(r"^[a-zA-Z\s]+$", message="Solo letras"),
        ],
    )

    apellido = StringField("Apellidos", validators=[Optional()])

    dni_cedula = StringField(
        "DNI RFC", validators=[DataRequired(message="Identificacion obligatoria")]
    )

    email = EmailField(
        "Correo",
        validators=[
            DataRequired(message="Correo obligatorio"),
            Email(message="Correo invalido"),
        ],
    )

    password = PasswordField(
        "Contrasena",
        validators=[
            DataRequired(message="Contrasena obligatoria"),
            Length(min=6, message="Minimo 6 caracteres"),
        ],
    )

    telefono = StringField(
        "Telefono",
        validators=[
            DataRequired(message="Telefono obligatorio"),
            Regexp(r"^[0-9]+$", message="Solo numeros"),
        ],
    )

    puesto = SelectField(
        "Puesto",
        choices=[
            ("GERENTE", "Gerente"),
            ("CHOCOLATERO", "Chocolatero"),
            ("CONTROL_CALIDAD", "Control de Calidad"),
            ("VENTAS", "Ventas"),
            ("LOGISTICA", "Logistica"),
            ("MANTENIMIENTO", "Mantenimiento"),
        ],
        validators=[DataRequired(message="Seleccione un puesto")],
    )

    salario_mensual = DecimalField(
        "Salario",
        places=2,
        default=0.00,
        validators=[
            DataRequired(message="Salario obligatorio"),
            NumberRange(min=0, message="No puede ser negativo"),
        ],
    )

    fecha_contratacion = DateField(
        "Fecha de Registro",
        [DataRequired(message="La fecha de registro es un campo obligatorio")],
        format="%Y-%m-%d",
    )

    imagen_empleado = FileField(
        "Foto",
        validators=[Optional(), FileAllowed(["jpg", "png", "jpeg"], "Solo imagenes")],
    )

    direccion = StringField("Direccion", validators=[Optional()])

    estatus = SelectField(
        "Estado Laboral",
        choices=[("ACTIVO", "ACTIVO"), ("INACTIVO", "INACTIVO")],
        validators=[DataRequired()],
    )
