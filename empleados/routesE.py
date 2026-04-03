import base64
from flask import render_template, request, redirect, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from . import empleado 
from models import db, Empleado
from .formsE import EmpleadoForm

def procesar_imagen_base64(archivo):
    if archivo and archivo.filename != '':
        contenido_binario = archivo.read()
        encoded_string = base64.b64encode(contenido_binario).decode('utf-8')
        return f"data:{archivo.content_type};base64,{encoded_string}"
    return None

@empleado.route('/empleados', methods=['GET'])
def empleadosAdmin(): 
    search_query = request.args.get('q', '').strip()
    query = Empleado.query
    if search_query:
        filtros = [
            Empleado.nombre.ilike(f"%{search_query}%"),
            Empleado.apellido.ilike(f"%{search_query}%"),
            Empleado.dni_cedula.ilike(f"%{search_query}%"),
            Empleado.puesto.ilike(f"%{search_query}%")
        ]
        query = query.filter(or_(*filtros))
    registros_empleados = query.all()
    return render_template("empleados/empleadosAdmin.html", 
                           empleados=registros_empleados, 
                           form=EmpleadoForm(),
                           query=search_query)

@empleado.route("/empleados/agregar", methods=["GET", "POST"])
def agregar_empleado():
    form = EmpleadoForm()
    if form.validate_on_submit():
        try:
            archivo_imagen = form.imagen_empleado.data
            imagen_data = procesar_imagen_base64(archivo_imagen) if archivo_imagen else None
            nuevo = Empleado(
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                dni_cedula=form.dni_cedula.data,
                email=form.email.data,
                telefono=form.telefono.data,
                puesto=form.puesto.data,
                salario_mensual=form.salario_mensual.data,
                fecha_contratacion=form.fecha_contratacion.data,
                direccion=form.direccion.data,
                imagen_empleado=imagen_data
            )
            db.session.add(nuevo)
            db.session.commit()
            return redirect(url_for('empleado.empleadosAdmin'))
        except IntegrityError as e:
            db.session.rollback()
            error_info = str(e.orig)
            if "dni_cedula" in error_info:
                form.dni_cedula.errors.append("Esta identificacion ya esta registrada.")
            elif "email" in error_info:
                form.email.errors.append("Este correo ya esta en uso.")
    return render_template("empleados/agregarEmpleados.html", form=form)

@empleado.route("/empleados/modificar/<int:id>", methods=["GET", "POST"])
def modificar_empleado(id):
    empleado_obj = Empleado.query.get_or_404(id)
    form = EmpleadoForm(obj=empleado_obj)
    fecha_string = empleado_obj.fecha_contratacion.strftime('%Y-%m-%d') if empleado_obj.fecha_contratacion else ""
    
    if form.validate_on_submit():
        try:
            archivo_input = request.files.get('imagen_empleado')
            nueva_imagen = procesar_imagen_base64(archivo_input) if archivo_input else None
            
            if nueva_imagen:
                empleado_obj.imagen_empleado = nueva_imagen
            
            form.populate_obj(empleado_obj)
            
            if 'estatus' in request.form:
                empleado_obj.estatus = request.form.get('estatus')
                
            db.session.commit()
            return redirect(url_for("empleado.empleadosAdmin"))
        except Exception:
            db.session.rollback()
            
    return render_template(
        "empleados/modificarEmpleados.html", 
        form=form, 
        empleado=empleado_obj, 
        empleado_id=id,
        fecha_string=fecha_string
    )

@empleado.route("/empleados/eliminar/<int:id>")
def eliminar_empleado(id):
    empleado_obj = Empleado.query.get_or_404(id)
    try:
        empleado_obj.estatus = 'INACTIVO'
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("empleado.empleadosAdmin"))

@empleado.route("/empleados/detalle/<int:id>")
def detalle_empleado(id):
    empleado_obj = Empleado.query.get_or_404(id)
    return render_template("empleados/detallesEmpleados.html", empleado=empleado_obj)