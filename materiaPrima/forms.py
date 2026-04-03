from wtforms import (
    Form,
    StringField,
    FloatField,
    SelectField,
    DateField,
    validators,
)


class MateriaPrimaForm(Form):
    nombre = StringField(
        "Nombre del Insumo",
        [
            validators.DataRequired(message="El nombre del insumo es obligatorio"),
            validators.Length(max=100, message="El nombre es demasiado largo"),
        ],
    )

    unidad_medida = StringField(
        "Unidad de Medida",
        [validators.DataRequired(message="Debes indicar la unidad (kg, gr, etc.)")],
    )

    stock_actual = FloatField(
        "Stock Actual",
        [validators.InputRequired(message="Ingresa la cantidad actual en inventario")],
    )

    stock_minimo = FloatField(
        "Stock Mínimo",
        [validators.InputRequired(message="El punto de reorden es obligatorio")],
    )

    costo_unitario = FloatField(
        "Costo Unitario",
        [
            validators.InputRequired(
                message="El costo por unidad es necesario para finanzas"
            )
        ],
    )

    porcentaje_merma = FloatField(
        "Porcentaje de Merma",
        [validators.InputRequired(message="Indica el % de pérdida (puedes poner 0)")],
    )

    descripcion = StringField(
        "Descripción", [validators.Optional(), validators.Length(max=200)]
    )

    fecha_ultima_compra = DateField(
        "Fecha Última Compra",
        [validators.DataRequired(message="La fecha es obligatoria para el historial")],
        format="%Y-%m-%d",
    )

    proveedor_id = SelectField(
        "Proveedor",
        coerce=int,
        validators=[
            validators.DataRequired(
                message="Debes seleccionar un proveedor de la lista"
            )
        ],
    )

    activo = SelectField(
        "Estado", choices=[(1, "Activo"), (0, "Inactivo")], coerce=int, default=1
    )
