from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
# --- SEGURIDAD Y USUARIOS ---
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    rol = db.Column(db.Enum('ADMIN', 'CLIENTE'), nullable=False, default='CLIENTE')
    activo = db.Column(db.Boolean, default=True)

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), unique=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    tipo = db.Column(db.Enum('MINORISTA', 'MAYORISTA'), default='MINORISTA')
    fecha_registro = db.Column(db.Date, default=datetime.utcnow)
    categoria_comprador = db.Column(db.Enum('OCASIONAL', 'FRECUENTE'), default='OCASIONAL')
    imagen_cliente = db.Column(db.String(500))
    notas = db.Column(db.String(200))

# --- ABASTECIMIENTO ---
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id_proveedor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    ruc = db.Column(db.String(20))
    notas = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.Date, default=datetime.utcnow)

class MateriaPrima(db.Model):
    __tablename__ = 'materias_primas'
    id_materia_prima = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    unidad_medida = db.Column(db.String(20), nullable=False)
    stock_actual = db.Column(db.Numeric(10, 2), default=0.00)
    stock_minimo = db.Column(db.Numeric(10, 2), default=10.00)
    costo_unitario = db.Column(db.Numeric(10, 2))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'))
    fecha_ultima_compra = db.Column(db.Date)
    porcentaje_merma = db.Column(db.Numeric(5, 2), default=0.00)
    imagen_materia = db.Column(db.String(500))
    activo = db.Column(db.Boolean, default=True)

# --- PRODUCCIÓN Y RECETAS ---
class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(200))
    categoria = db.Column(db.String(50))
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    costo_produccion_estimado = db.Column(db.Numeric(10, 2))
    unidad_medida = db.Column(db.String(20), default='unidad')
    stock_actual = db.Column(db.Numeric(10, 2), default=0.00)
    stock_minimo = db.Column(db.Numeric(10, 2), default=10.00)
    tiempo_produccion_minutos = db.Column(db.Integer)
    receta = db.Column(db.String(200)) # Notas generales
    imagen_producto = db.Column(db.String(500))
    activo = db.Column(db.Boolean, default=True)

class Receta(db.Model):
    __tablename__ = 'recetas'
    id_receta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    nombre_receta = db.Column(db.String(100))
    cantidad_lote = db.Column(db.Integer, default=1)
    instrucciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

class RecetaDetalle(db.Model):
    __tablename__ = 'recetas_detalle'
    id_receta_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id_receta'), nullable=False)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materia_prima'), nullable=False)
    cantidad_necesaria = db.Column(db.Numeric(10, 2), nullable=False)

class OrdenProduccion(db.Model):
    __tablename__ = 'ordenes_produccion'
    id_orden_produccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad_requerida = db.Column(db.Integer, nullable=False)
    fecha_inicio = db.Column(db.DateTime)
    fecha_fin = db.Column(db.DateTime)
    estado = db.Column(db.Enum('PENDIENTE', 'EN_PROCESO', 'COMPLETADA', 'CANCELADA'), default='PENDIENTE')
    lote = db.Column(db.String(50), unique=True)
    prioridad = db.Column(db.Enum('BAJA', 'MEDIA', 'ALTA', 'URGENTE'), default='MEDIA')
    observaciones = db.Column(db.String(200))
    costo_total_real = db.Column(db.Numeric(12, 2))
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id_receta'))

# --- VENTAS Y MOVIMIENTOS ---
class Venta(db.Model):
    __tablename__ = 'ventas'
    id_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'))
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    subtotal = db.Column(db.Numeric(12, 2))
    impuestos = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2), default=0.00)
    metodo_pago = db.Column(db.Enum('EFECTIVO', 'TARJETA'), nullable=False)
    estado = db.Column(db.Enum('PENDIENTE', 'COMPLETADA', 'CANCELADA', 'DEVUELTA'), default='COMPLETADA')
    canal = db.Column(db.Enum('TIENDA', 'WEB', 'OTRA'), default='TIENDA')
    empleado = db.Column(db.String(50))
    observaciones = db.Column(db.String(200))
    utilidad_total = db.Column(db.Numeric(12, 2))
    costo_total_ventas = db.Column(db.Numeric(12, 2))

class DetalleVenta(db.Model):
    __tablename__ = 'detalles_ventas'
    id_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id_venta'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    costo_unitario_momento_venta = db.Column(db.Numeric(10, 2))

class CompraMateriaPrima(db.Model):
    __tablename__ = 'compras_materia_prima'
    id_compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materia_prima'), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_compra = db.Column(db.DateTime, default=datetime.utcnow)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'))
    observaciones = db.Column(db.String(200))

class PagoProveedor(db.Model):
    __tablename__ = 'pagos_proveedores'
    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    metodo_pago = db.Column(db.Enum('EFECTIVO', 'TRANSFERENCIA'), default='EFECTIVO')
    compra_id = db.Column(db.Integer, db.ForeignKey('compras_materia_prima.id_compra'))
    numero_comprobante = db.Column(db.String(50))
    observaciones = db.Column(db.String(200))
    usuario_registro = db.Column(db.String(50))

class MovimientoInventario(db.Model):
    __tablename__ = 'inventario_movimientos'
    id_movimiento = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    tipo_movimiento = db.Column(db.String(20), nullable=False) # ENTRADA, SALIDA, AJUSTE
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.String(50))
    fecha_movimiento = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación para poder ver el nombre del producto en el historial
    producto = db.relationship('Producto', backref='movimientos')    