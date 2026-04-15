from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class FormOrdenProduccion(FlaskForm):
    producto_id = SelectField(
        "Producto a Fabricar", coerce=int, validators=[DataRequired()]
    )
    cantidad_requerida = IntegerField(
        "Cantidad", validators=[DataRequired(), NumberRange(min=1)]
    )
    prioridad = SelectField(
        "Prioridad",
        choices=[
            ("BAJA", "Baja"),
            ("MEDIA", "Media"),
            ("ALTA", "Alta"),
            ("URGENTE", "Urgente"),
        ],
    )
    submit = SubmitField("Crear Orden")
