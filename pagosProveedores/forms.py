from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, Regexp, ValidationError


class PagoProveedorForm(FlaskForm):
    accion = SelectField(
        'Acción',
        choices=[
            ('PAGADO', 'Marcar como pagado'),
            ('CANCELADO', 'Cancelar compra')
        ],
        validators=[DataRequired(message='Debes seleccionar una acción.')]
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

    numero_comprobante = StringField(
        'Número de comprobante',
        validators=[
            Optional(),
            Length(max=50, message='El número de comprobante no debe exceder 50 caracteres.'),
            Regexp(
                r'^[A-Za-z0-9\-\/]+$',
                message='El comprobante solo puede contener letras, números, guiones y diagonales.'
            )
        ]
    )

    observaciones = TextAreaField(
        'Observaciones',
        validators=[
            Optional(),
            Length(max=300, message='Las observaciones no deben exceder 300 caracteres.')
        ]
    )

    submit = SubmitField('Guardar')

    def validate_metodo_pago(self, field):
        if self.accion.data == 'PAGADO' and not field.data:
            raise ValidationError('Debes seleccionar un método de pago cuando la compra se marque como pagada.')

        if self.accion.data == 'CANCELADO' and field.data:
            raise ValidationError('No debes seleccionar método de pago si la compra será cancelada.')

    def validate_numero_comprobante(self, field):
        if self.accion.data == 'PAGADO' and self.metodo_pago.data == 'TRANSFERENCIA' and not field.data.strip():
            raise ValidationError('Debes capturar el número de comprobante para pagos por transferencia.')

        if self.accion.data == 'CANCELADO' and field.data.strip():
            raise ValidationError('No debes capturar comprobante si la compra será cancelada.')

    def validate_observaciones(self, field):
        texto = field.data.strip() if field.data else ''
        if texto and len(texto) < 3:
            raise ValidationError('Las observaciones deben tener al menos 3 caracteres si se capturan.')