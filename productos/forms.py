from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from decimal import Decimal
import re


class ProductoForm(FlaskForm):
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es obligatorio'),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres')
        ]
    )

    descripcion = TextAreaField(
        'Descripción',
        validators=[
            Optional(),
            Length(max=200, message='La descripción no debe exceder 200 caracteres')
        ]
    )

    categoria = StringField(
        'Categoría',
        validators=[
            DataRequired(message='La categoria es obligatoria'),
            Length(max=50, message='La categoría no debe exceder 50 caracteres')
        ]
    )

    precio_venta = DecimalField(
        'Precio de venta',
        validators=[
            DataRequired(message='El precio de venta es obligatorio'),
            NumberRange(min=0.01, max=10000, message='El precio debe estar entre 0.01 y 999999.99')
        ],
        places=2
    )

    costo_produccion_estimado = DecimalField(
        'Costo de producción estimado',
        validators=[
            DataRequired(message='El costo de producción es obligatorio'),
            NumberRange(min=0, max=10000000, message='Coloca el costo correctamente')
        ],
        places=2
    )

    unidad_medida = SelectField(
    'Unidad de medida',
    choices=[
        ('', 'Selecciona una unidad'),
        ('pieza', 'Pieza'),
        ('kg', 'Kilogramo'),
        ('g', 'Gramo'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('caja', 'Caja'),
        ('paquete', 'Paquete'),
        ('barra', 'Barra')
    ],
    validators=[DataRequired(message='La unidad de medida es obligatorio')]
)

    tiempo_produccion_minutos = IntegerField(
        'Tiempo de producción (minutos)',
        validators=[
            Optional(),
            NumberRange(min=0, max=10080, message='El tiempo debe estar entre 0 y 10080 minutos')
        ]
    )

    imagen_producto = FileField(
        'Imagen del producto',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo se permiten imágenes JPG, JPEG, PNG o WEBP')
        ]
    )

    activo = BooleanField('Activo', default=True)

    submit = SubmitField('Guardar')

    def validate_nombre(self, field):
        field.data = field.data.strip()

        if not field.data:
            raise ValidationError('El nombre no puede estar vacío.')

        if re.fullmatch(r'[\W_]+', field.data):
            raise ValidationError('El nombre no puede contener solo símbolos.')

        if re.search(r'\s{2,}', field.data):
            raise ValidationError('El nombre no debe contener espacios dobles.')

        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\-\.,()%]+", field.data):
            raise ValidationError('El nombre contiene caracteres no permitidos.')

    def validate_descripcion(self, field):
        if field.data:
            field.data = field.data.strip()

            if re.fullmatch(r'[\W_]+', field.data):
                raise ValidationError('La descripción no puede contener solo símbolos.')

            if re.search(r'\s{3,}', field.data):
                raise ValidationError('La descripción contiene demasiados espacios seguidos.')

    def validate_categoria(self, field):
        if field.data:
            field.data = field.data.strip()

            if re.fullmatch(r'[\W_]+', field.data):
                raise ValidationError('La categoría no puede contener solo símbolos.')

            if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\-]+", field.data):
                raise ValidationError('La categoría contiene caracteres no permitidos.')

    def validate_unidad_medida(self, field):
        if field.data:
            field.data = field.data.strip().lower()

            unidades_validas = [
                'pieza', 'piezas', 'kg', 'g', 'mg', 'l', 'ml',
                'caja', 'cajas', 'paquete', 'paquetes',
                'botella', 'botellas', 'bolsa', 'bolsas',
                'barra', 'barras'
            ]

            if field.data not in unidades_validas:
                raise ValidationError('Selecciona o escribe una unidad de medida válida.')

    def validate_precio_venta(self, field):
        if field.data is None:
            raise ValidationError('El precio de venta es obligatorio.')

        if field.data <= Decimal('0'):
            raise ValidationError('El precio de venta debe ser mayor a 0.')

    def validate_costo_produccion_estimado(self, field):
        if field.data is not None and field.data < Decimal('0'):
            raise ValidationError('El costo de producción no puede ser negativo.')

    def validate_tiempo_produccion_minutos(self, field):
        if field.data is not None and field.data < 0:
            raise ValidationError('El tiempo de producción no puede ser negativo.')