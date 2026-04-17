from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, Regexp, ValidationError


class PagoProveedorForm(FlaskForm):
    accion = SelectField(
        "Acción",
        choices=[("PAGADO", "Marcar como pagado"), ("CANCELADO", "Cancelar compra")],
        validators=[DataRequired(message="Debes seleccionar una acción.")],
    )

    metodo_pago = SelectField(
        "Método de pago",
        choices=[
            ("", "Selecciona un método"),
            ("EFECTIVO", "Efectivo"),
            ("TRANSFERENCIA", "Transferencia"),
        ],
        validators=[Optional()],
    )

    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=300)])
    submit = SubmitField("Guardar")

    # SOLO dejamos la validación del método de pago
    def validate_metodo_pago(self, field):
        if self.accion.data == "PAGADO" and not field.data:
            raise ValidationError("Selecciona un método de pago para registrar la compra.")

        if self.accion.data == "CANCELADO" and field.data:
            raise ValidationError("No debes seleccionar método de pago si la compra será cancelada.")