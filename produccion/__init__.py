from flask import Blueprint

produccion = Blueprint("produccion", __name__, template_folder="templates")

from . import routes
