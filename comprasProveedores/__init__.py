# comprasProveedores/__init__.py
from flask import Blueprint

compras_bp = Blueprint("comprasProveedores", __name__, template_folder="templates")

from . import routes
