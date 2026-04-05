from flask import Blueprint
gesVentas = Blueprint("gesVentas", __name__, template_folder="templates")
from . import routes