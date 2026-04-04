from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, DecimalField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class FormVenta(FlaskForm):
    producto_id = SelectField('Producto', coerce=int, validators=[DataRequired()])
    cliente_id = SelectField('Cliente', coerce=int)
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    metodo_pago = SelectField('Método de Pago', choices=[('EFECTIVO', 'Efectivo'), ('TARJETA', 'Tarjeta')])
    submit = SubmitField('Confirmar Venta')

class FormPagoProveedor(FlaskForm):
    proveedor_id = SelectField('Proveedor', coerce=int, validators=[DataRequired()])
    monto = DecimalField('Monto a Pagar', places=2, validators=[DataRequired()])
    metodo_pago = SelectField('Método', choices=[('EFECTIVO', 'Efectivo'), ('TRANSFERENCIA', 'Transferencia')])
    observaciones = StringField('Observaciones')
    submit = SubmitField('Registrar Pago')