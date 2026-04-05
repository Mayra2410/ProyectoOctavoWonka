from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class PagoProveedorForm(FlaskForm):

    accion = SelectField(
        'Acción',
        choices=[
            ('PAGADO', 'Marcar como pagado'),
            ('CANCELADO', 'Cancelar compra')
        ],
        validators=[DataRequired()]
    )

    metodo_pago = SelectField(
        'Método de pago',
        choices=[
            ('', 'Selecciona un método'),
            ('EFECTIVO', 'Efectivo'),
            ('TRANSFERENCIA', 'Transferencia')
        ],
        validators=[Optional()]
    )

    numero_comprobante = StringField('Número de comprobante', validators=[Optional()])
    observaciones = TextAreaField('Observaciones', validators=[Optional()])

    submit = SubmitField('Guardar')