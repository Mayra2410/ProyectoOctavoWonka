from wtforms import (
    Form,
    StringField,
    IntegerField,
    DecimalField,
    TextAreaField,
    SelectField,
    validators,
    DateTimeField,
)


class CompraMateriaPrimaForm(Form):
    materia_prima_id = SelectField(
        "Insumo / Materia Prima",
        coerce=int,
        validators=[validators.DataRequired(message="Selecciona un insumo")],
    )

    proveedor_id = SelectField(
        "Proveedor",
        coerce=int,
        validators=[validators.DataRequired(message="Selecciona un proveedor")],
    )

    cantidad = DecimalField(
        "Cantidad Comprada",
        [
            validators.DataRequired(message="Ingresa la cantidad"),
            validators.NumberRange(min=0.01),
        ],
        places=2,
    )

    costo_unitario = DecimalField(
        "Costo Unitario",
        [validators.DataRequired(message="Ingresa el costo")],
        places=2,
    )

    fecha_compra = DateTimeField(
        "Fecha de Compra",
        [validators.DataRequired(message="Selecciona la fecha y hora")],
        format="%Y-%m-%d %H:%M",  # Formato: Año-Mes-Día Hora:Minuto
    )

    observaciones = TextAreaField(
        "Notas de la Compra", [validators.Optional(), validators.Length(max=200)]
    )
