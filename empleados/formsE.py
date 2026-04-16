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
    ValidationError,
)
from models import Usuario, Empleado


class EmpleadoForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio"),
            Length(min=3, message="Minimo 3 caracteres"),
            Regexp(r"^[a-zA-Z\s]+$", message="Solo se aceptan letras"),
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
        "Contrasena", validators=[DataRequired(message="Contrasena obligatoria")]
    )

    telefono = StringField(
        "Telefono",
        validators=[
            DataRequired(message="Telefono obligatorio"),
            Regexp(r"^[0-9]+$", message="Solo se aceptan numeros"),
        ],
    )

    puesto = SelectField(
        "Puesto",
        choices=[
            ("GERENTE", "Gerente"),
            ("CHOCOLATERO", "Chocolatero"),
            ("CONTROL_CALIDAD", "Control de Calidad"),
            ("VENTAS", "Ventas"),
            ("LOGISTICA", "Logística"),
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
        validators=[
            DataRequired(message="La foto es obligatoria"),
            FileAllowed(["jpg", "png", "jpeg"], "Solo se aceptan formatos JPG, PNG o JPEG")
        ],
    )

    direccion = StringField("Direccion", validators=[Optional()])

    estatus = SelectField(
        "Estado Laboral",
        choices=[("ACTIVO", "ACTIVO"), ("INACTIVO", "INACTIVO")],
        validators=[DataRequired()],
    )

    def validate_email(self, email):
        if email.data:
            existente = Usuario.query.filter_by(email=email.data).first()
            if existente:
                raise ValidationError("Este correo ya esta registrado en el sistema.")

    def validate_dni_cedula(self, dni_cedula):
        if dni_cedula.data:
            existente = Empleado.query.filter_by(dni_cedula=dni_cedula.data).first()
            if existente:
                raise ValidationError(
                    "Esta identificacion (DNI/RFC) ya esta duplicada."
                )
