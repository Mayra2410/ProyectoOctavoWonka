from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductoForm(FlaskForm):
    nombre = StringField(
        'Nombre',
        validators=[DataRequired(message='El nombre es obligatorio'), Length(max=100)]
    )

    descripcion = TextAreaField(
        'Descripción',
        validators=[Optional(), Length(max=200)]
    )

    categoria = StringField(
        'Categoría',
        validators=[Optional(), Length(max=50)]
    )

    precio_venta = DecimalField(
        'Precio de venta',
        validators=[DataRequired(message='El precio es obligatorio'), NumberRange(min=0)],
        places=2
    )

    costo_produccion_estimado = DecimalField(
        'Costo de producción estimado',
        validators=[Optional(), NumberRange(min=0)],
        places=2
    )

    unidad_medida = StringField(
        'Unidad de medida',
        validators=[Optional(), Length(max=20)]
    )

    tiempo_produccion_minutos = IntegerField(
        'Tiempo de producción (minutos)',
        validators=[Optional(), NumberRange(min=0)]
    )

    imagen_producto = FileField(
        'Imagen del producto',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo se permiten imágenes')
        ]
    )

    activo = BooleanField('Activo', default=True)

    submit = SubmitField('Guardar')