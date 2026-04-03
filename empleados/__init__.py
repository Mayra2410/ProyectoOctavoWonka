
from flask import Blueprint

empleado = Blueprint(
    'empleado',
    __name__,
    template_folder='templates'
)

from . import routesE