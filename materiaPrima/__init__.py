from flask import Blueprint

materia_Prima = Blueprint("materiaPrima", __name__, template_folder="templates")

from . import routes
