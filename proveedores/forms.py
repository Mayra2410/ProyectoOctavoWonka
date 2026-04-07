from wtforms import (
    Form,
    StringField,
    IntegerField,
    TextAreaField,
    SelectField,
    DateField,
    EmailField,
)
from wtforms import validators


class ProveedorForm(Form):
    id_proveedor = IntegerField("ID", [validators.Optional()])

    nombre = StringField(
        "Nombre de la Empresa",
        [
            validators.DataRequired(message="El nombre es requerido"),
            validators.Length(min=3, max=100, message="Nombre demasiado corto o largo"),
        ],
    )

    contacto = StringField(
        "Nombre del Contacto",
        [
            validators.DataRequired(message="El contacto es requerido"),
            validators.Length(max=100),
        ],
    )

    telefono = StringField(
        "Teléfono",
        [
            validators.DataRequired(message="El teléfono es requerido"),
            validators.Length(max=20),
            validators.Regexp(
                r'^\+?[0-9]+$', 
                message="El teléfono solo debe contener números (sin espacios)"
            )
        ],
    )

    email = EmailField(
        "Correo Electrónico",
        [
            validators.DataRequired(message="El correo es requerido"),
            validators.Email(message="Ingresa un correo válido"),
        ],
    )

    direccion = StringField(
        "Dirección",
        [
            validators.DataRequired(message="La dirección es requerida"),
            validators.Length(max=200),
        ],
    )

    ruc = StringField(
        "RUC / Registro Fiscal",
        [
            validators.DataRequired(message="El RUC es requerido"),
            validators.Length(min=8, max=20, message="RUC no válido"),
        ],
    )

    notas = TextAreaField(
        "Notas Adicionales", [validators.Optional(), validators.Length(max=200)]
    )

    activo = SelectField(
        "Estado", choices=[(1, "Activo"), (0, "Inactivo")], coerce=int, default=1
    )

    fecha_registro = DateField(
        "Fecha de Registro",
        [validators.DataRequired(message="Selecciona una fecha")],
        format="%Y-%m-%d",
    )
