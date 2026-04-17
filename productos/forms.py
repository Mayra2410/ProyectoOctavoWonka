from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    IntegerField,
    SelectField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)
import re


class ProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre del producto",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(
                min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres."
            ),
        ],
    )

    descripcion = TextAreaField(
        "Descripción",
        validators=[
            Optional(),
            Length(
                max=500, message="La descripción no puede exceder los 500 caracteres."
            ),
        ],
    )

    categoria = StringField(
        "Categoría",
        validators=[
            DataRequired(message="La categoría es obligatoria."),
            Length(
                min=3,
                max=50,
                message="La categoría debe tener entre 3 y 50 caracteres.",
            ),
        ],
    )

    precio_venta = DecimalField(
        "Precio de venta",
        places=2,
        validators=[
            DataRequired(message="El precio de venta es obligatorio."),
            NumberRange(min=0, message="El precio de venta no puede ser negativo."),
        ],
    )

    costo_produccion_estimado = DecimalField(
        "Costo de producción estimado",
        places=2,
        validators=[
            DataRequired(message="El costo de producción es obligatorio."),
            NumberRange(min=0, message="El costo de producción no puede ser negativo."),
        ],
    )

    unidad_medida = SelectField(
        "Unidad de medida",
        choices=[
            ("Pieza", "Pieza"),
        ],
        default="Pieza",
        validators=[DataRequired()],
    )

    tiempo_produccion_minutos = IntegerField(
        "Tiempo de producción (minutos)",
        validators=[
            DataRequired(message="El tiempo de producción es obligatorio."),
            NumberRange(min=1, message="El tiempo de producción debe ser mayor a 0."),
        ],
    )

    imagen_producto = FileField("Imagen del producto", validators=[Optional()])

    activo = BooleanField("Producto activo", validators=[Optional()])

    submit = SubmitField("Guardar")

    def validate_nombre(self, field):
        field.data = field.data.strip()

        if not field.data:
            raise ValidationError("El nombre no puede estar vacío.")

        if re.fullmatch(r"[\W_]+", field.data):
            raise ValidationError("El nombre no puede contener solo símbolos.")

        if re.search(r" {2,}", field.data):
            raise ValidationError("No se permiten espacios dobles.")

        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\-\.,()%+/°]+", field.data):
            raise ValidationError("El nombre contiene caracteres no permitidos.")

    def validate_categoria(self, field):
        field.data = field.data.strip()

        if not field.data:
            raise ValidationError("La categoría no puede estar vacía.")

        if re.fullmatch(r"[\W_]+", field.data):
            raise ValidationError("La categoría no puede contener solo símbolos.")

    def validate_descripcion(self, field):
        if field.data:
            field.data = field.data.strip()

            if re.fullmatch(r"[\W_]+", field.data):
                raise ValidationError("La descripción no puede contener solo símbolos.")
