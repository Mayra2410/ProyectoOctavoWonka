from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange,
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

    cantidad_lote = IntegerField(
        "Cantidad por lote",
        validators=[
            DataRequired(message="La cantidad por lote es obligatoria"),
            NumberRange(min=1, max=100000, message="La cantidad debe ser mayor a 0"),
        ],
    )

    instrucciones = TextAreaField(
        "Instrucciones",
        validators=[
            Optional(),
            Length(
                max=500, message="Las instrucciones no deben exceder 500 caracteres"
            ),
        ],
    )

    activo = BooleanField("Activo", default=True)

    submit = SubmitField("Guardar")

    def validate_nombre_receta(self, field):
        field.data = field.data.strip()

        if not field.data:
            raise ValidationError("El nombre no puede estar vacío.")

        if re.fullmatch(r"[\W_]+", field.data):
            raise ValidationError("El nombre no puede contener solo símbolos.")

        if re.search(r"\s{2,}", field.data):
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

            if re.search(r"\s{3,}", field.data):
                raise ValidationError("Hay demasiados espacios consecutivos.")

    def validate_producto_id(self, field):
        if field.data is None or field.data == 0:
            raise ValidationError("Debes seleccionar un producto válido.")

    def validate_cantidad_lote(self, field):
        if field.data is None:
            raise ValidationError("La cantidad es obligatoria.")

        if field.data <= 0:
            raise ValidationError("Debe ser mayor a 0.")

        if field.data > 100000:
            raise ValidationError("Cantidad demasiado alta.")
