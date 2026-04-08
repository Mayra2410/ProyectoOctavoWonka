from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class FormAjusteInventario(FlaskForm):
    producto_id = SelectField("Producto", coerce=int, validators=[DataRequired()])
    cantidad = IntegerField(
        "Cantidad de Ajuste (puede ser negativa)", validators=[DataRequired()]
    )
    motivo = StringField("Motivo del Ajuste", validators=[DataRequired()])
    submit = SubmitField("Registrar Ajuste")
