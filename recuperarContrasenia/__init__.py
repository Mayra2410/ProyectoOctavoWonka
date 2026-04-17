from flask import Blueprint

recuperarContrasenia = Blueprint(
    "recuperarContrasenia", __name__, template_folder="templates"
)

from . import routesRC
