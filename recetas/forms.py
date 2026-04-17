from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    ValidationError,
)
import re


class RecetaForm(FlaskForm):

    nombre_receta = StringField(
        "Nombre de la receta",
        validators=[
            DataRequired(message="El nombre de la receta es obligatorio"),
            Length(min=3, max=100, message="Debe tener entre 3 y 100 caracteres"),
        ],
    )

    producto_id = SelectField(
        "Producto",
        coerce=int,
        validators=[DataRequired(message="Debes seleccionar un producto válido")],
    )

    instrucciones = TextAreaField(
        "Instrucciones",
        validators=[Optional()],
    )

    activo = SelectField(
        "Estado",
        choices=[("1", "ACTIVO"), ("0", "INACTIVO")],
        validators=[Optional()],
    )

    submit = SubmitField("Guardar")

    def validate_nombre_receta(self, field):
        field.data = field.data.strip()

        if not field.data:
            raise ValidationError("El nombre no puede estar vacío.")

        if re.fullmatch(r"[\W_]+", field.data):
            raise ValidationError("El nombre no puede contener solo símbolos.")

        if re.search(r" {2,}", field.data):
            raise ValidationError("No se permiten espacios dobles.")

        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\-\.,()%+/°]+", field.data):
            raise ValidationError("El nombre contiene caracteres no permitidos.")

    def validate_instrucciones(self, field):
        if field.data:
            field.data = field.data.strip()

            if re.fullmatch(r"[\W_]+", field.data):
                raise ValidationError(
                    "Las instrucciones no pueden contener solo símbolos."
                )

            if re.search(r" {3,}", field.data):
                raise ValidationError("Hay demasiados espacios consecutivos.")

    def validate_producto_id(self, field):
        if field.data is None or field.data == 0:
            raise ValidationError("Debes seleccionar un producto válido.")
