from flask import Blueprint

registro = Blueprint("registro", __name__, template_folder="templates")

from . import routesR
