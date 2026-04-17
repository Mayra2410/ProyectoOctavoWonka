from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    FloatField,
    SelectField,
    DateField,
    validators,
    TextAreaField,
)
from flask_wtf.file import FileField, FileAllowed
from flask import request


class MateriaPrimaForm(FlaskForm):
    nombre = StringField(
        "Nombre del Insumo",
        [
            validators.DataRequired(message="El nombre del insumo es obligatorio"),
            validators.Length(max=100, message="El nombre es demasiado largo"),
        ],
    )

    unidad_medida = SelectField(
        "Unidad de Medida",
        choices=[
            ("", "Selecciona una unidad..."),
            ("kg", "Kilogramos (kg)"),
            ("gr", "Gramos (gr)"),
            ("lt", "Litros (lt)"),
            ("ml", "Mililitros (ml)"),
            ("pza", "Piezas (pza)"),
        ],
        validators=[validators.DataRequired(message="Debes seleccionar una unidad")],
    )

    stock_actual = FloatField(
        "Stock Actual",
        [
            validators.InputRequired(message="Ingresa la cantidad actual"),
            validators.NumberRange(min=0, message="El stock no puede ser negativo"),
        ],
    )

    stock_minimo = FloatField(
        "Stock Mínimo",
        [
            validators.InputRequired(message="El punto de reorden es obligatorio"),
            validators.NumberRange(min=0, message="El mínimo no puede ser negativo"),
        ],
    )

    costo_unitario = FloatField(
        "Costo Unitario",
        [
            validators.InputRequired(message="El costo es necesario"),
            validators.NumberRange(min=0.01, message="El costo debe ser mayor a 0"),
        ],
    )

    porcentaje_merma = FloatField(
        "Porcentaje de Merma",
        [
            validators.InputRequired(message="Indica el % de pérdida"),
            validators.NumberRange(min=0, max=100, message="Debe estar entre 0 y 100"),
        ],
    )

    descripcion = TextAreaField(
        "Descripción", [validators.Optional(), validators.Length(max=200)]
    )

    fecha_ultima_compra = DateField(
        "Fecha Última Compra",
        [validators.DataRequired(message="La fecha es obligatoria")],
        format="%Y-%m-%d",
    )

    proveedor_id = SelectField(
        "Proveedor",
        coerce=int,
        validators=[validators.DataRequired(message="Selecciona un proveedor")],
    )

    activo = SelectField(
        "Estado", choices=[(1, "Activo"), (0, "Inactivo")], coerce=int, default=1
    )

    imagen_materia = FileField(
        "Fotografía del Insumo",
        validators=[
            FileAllowed(
                ["jpg", "png", "jpeg"], message="Solo se permiten imágenes (jpg, png)"
            )
        ],
    )

    def validate_imagen_materia(self, field):
        archivo = request.files.get(field.name)
        if "agregar" in request.endpoint:
            if not archivo or archivo.filename == "":
                raise validators.ValidationError("La fotografía es obligatoria")