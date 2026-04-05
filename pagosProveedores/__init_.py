from flask import Blueprint

pagosProveedores = Blueprint(
    'pagosProveedores',
    __name__
)

from . import routes