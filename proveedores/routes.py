from flask import render_template
from . import proveedores


@proveedores.route("/proveedores")  
def lista_proveedores():  
    return render_template("proveedores/proveedoresAdmin.html")
