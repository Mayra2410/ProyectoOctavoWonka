from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class RecetaForm(FlaskForm):
    nombre_receta = StringField(
        'Nombre de la receta',
        validators=[DataRequired(message='El nombre de la receta es obligatorio'), Length(max=100)]
    )

    producto_id = SelectField(
        'Producto',
        coerce=int,
        validators=[DataRequired(message='Debes seleccionar un producto')]
    )

    cantidad_lote = IntegerField(
        'Cantidad por lote',
        validators=[DataRequired(message='La cantidad por lote es obligatoria'), NumberRange(min=1)]
    )

    instrucciones = TextAreaField(
        'Instrucciones',
        validators=[Optional()]
    )

    activo = BooleanField('Activo', default=True)

    submit = SubmitField('Guardar')