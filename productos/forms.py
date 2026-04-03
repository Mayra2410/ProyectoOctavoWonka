from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, BooleanField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Optional

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    categoria = StringField('Categoría', validators=[Optional()])
    precio_venta = DecimalField('Precio', validators=[DataRequired()])
    costo_produccion_estimado = DecimalField('Costo', validators=[Optional()])
    unidad_medida = StringField('Unidad', validators=[Optional()])
    tiempo_produccion_minutos = IntegerField('Tiempo', validators=[Optional()])

    imagen = FileField('Imagen', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imágenes')
    ])

    activo = BooleanField('Activo', default=True)