from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

# --- 1. SEGURIDAD Y USUARIOS ---
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
    fecha_registro = db.Column(db.Date, default=date.today)
    categoria_comprador = db.Column(db.Enum('OCASIONAL', 'FRECUENTE'), default='OCASIONAL')
    imagen_cliente = db.Column(db.String(500))
    notas = db.Column(db.String(200))

# --- 2. ABASTECIMIENTO (Nomenclatura Victor: Plural) ---
class Proveedores(db.Model):
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
    fecha_registro = db.Column(db.Date, default=date.today)

    # Relación con MateriasPrimas
    materias = db.relationship("MateriasPrimas", backref="proveedor", lazy=True)

class MateriasPrimas(db.Model):
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
    imagen_materia = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    # Relación para Recetas (Victor)
    detalles_receta = db.relationship("RecetaDetalle", back_populates="materia_prima", cascade="all, delete-orphan")

# --- 3. PRODUCCIÓN Y RECETAS ---
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
    imagen_producto = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    recetas = db.relationship("Receta", back_populates="producto", cascade="all, delete-orphan")

class Receta(db.Model):
    __tablename__ = 'recetas'
    id_receta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    nombre_receta = db.Column(db.String(100), nullable=False)
    cantidad_lote = db.Column(db.Integer, default=1)
    instrucciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

    producto = db.relationship("Producto", back_populates="recetas")
    detalles = db.relationship("RecetaDetalle", back_populates="receta", cascade="all, delete-orphan")

class RecetaDetalle(db.Model):
    __tablename__ = 'recetas_detalle'
    id_receta_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id_receta'), nullable=False)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materia_prima'), nullable=False)
    cantidad_necesaria = db.Column(db.Numeric(10, 2), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False)

    receta = db.relationship("Receta", back_populates="detalles")
    materia_prima = db.relationship("MateriasPrimas", back_populates="detalles_receta")

class OrdenProduccion(db.Model):
    __tablename__ = 'ordenes_produccion'
    id_orden_produccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad_requerida = db.Column(db.Integer, nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.now)
    fecha_fin = db.Column(db.DateTime)
    estado = db.Column(db.Enum('PENDIENTE', 'EN_PROCESO', 'COMPLETADA', 'CANCELADA'), default='PENDIENTE')
    lote = db.Column(db.String(50), unique=True)
    prioridad = db.Column(db.Enum('BAJA', 'MEDIA', 'ALTA', 'URGENTE'), default='MEDIA')
    observaciones = db.Column(db.String(200))
    usuario_inicio = db.Column(db.String(50))
    usuario_fin = db.Column(db.String(50))

# --- 4. VENTAS E INVENTARIO (Trazabilidad y Auditoría) ---
class Venta(db.Model):
    __tablename__ = 'ventas'
    id_venta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'))
    fecha_venta = db.Column(db.DateTime, default=datetime.now)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    metodo_pago = db.Column(db.Enum('EFECTIVO', 'TARJETA'), nullable=False)
    estado = db.Column(db.Enum('PENDIENTE', 'COMPLETADA', 'CANCELADA'), default='COMPLETADA')

class ComprasMateriaPrima(db.Model):
    __tablename__ = 'compras_materia_prima'
    id_compra = db.Column(db.Integer, primary_key=True, autoincrement=True)
    materia_prima_id = db.Column(db.Integer, db.ForeignKey('materias_primas.id_materia_prima'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'), nullable=False)
    cantidad = db.Column(db.Numeric(10, 2), nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_compra = db.Column(db.DateTime, default=datetime.now)
    # Dentro de class ComprasMateriaPrima(db.Model):
    materia_prima = db.relationship("MateriasPrimas", backref="compras")
    proveedor_rel = db.relationship("Proveedores", backref="compras_rel")
    estatus_compra = db.Column(db.Enum('PENDIENTE', 'PAGADO', 'CANCELADO'), default='PENDIENTE')

    pagos = db.relationship("PagoProveedor", back_populates="compra", cascade="all, delete-orphan")

class PagoProveedor(db.Model):
    __tablename__ = 'pagos_proveedores'
    id_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compras_materia_prima.id_compra'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id_proveedor'), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.now)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    metodo_pago = db.Column(db.Enum('EFECTIVO', 'TRANSFERENCIA'), nullable=False)
    
    compra = db.relationship("ComprasMateriaPrima", back_populates="pagos")

class MovimientoInventario(db.Model):
    __tablename__ = 'inventario_movimientos'
    id_movimiento = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    tipo_movimiento = db.Column(db.String(20), nullable=False) # ENTRADA, SALIDA, AJUSTE
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.String(50))
    fecha_movimiento = db.Column(db.DateTime, default=datetime.now)

    producto = db.relationship('Producto', backref='movimientos')