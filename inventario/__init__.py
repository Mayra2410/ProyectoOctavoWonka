from flask import Blueprint
inventario = Blueprint("inventario", __name__, template_folder="templates")
from . import routes