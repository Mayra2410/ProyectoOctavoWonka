import base64
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from . import empleado 
from models import db, Empleado, Usuario
from .formsE import EmpleadoForm
from werkzeug.security import generate_password_hash
from datetime import datetime

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

import base64
from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from . import empleado 
from models import db, Empleado, Usuario
from .formsE import EmpleadoForm
from werkzeug.security import generate_password_hash
from datetime import datetime

def procesar_imagen_base64(archivo):
    if archivo and archivo.filename != '':
        contenido_binario = archivo.read()
        encoded_string = base64.b64encode(contenido_binario).decode('utf-8')
        return f"data:{archivo.content_type};base64,{encoded_string}"
    return None

@empleado.route('/agregar_empleado', methods=['GET', 'POST'])
def agregar_empleado():
    form = EmpleadoForm()
    
    if request.method == 'POST':
        if not form.estatus.data:
            form.estatus.data = 'ACTIVO'

        if form.validate_on_submit():
            usuario_existente = Usuario.query.filter_by(email=form.email.data).first()
            if usuario_existente:
                flash(f"El correo {form.email.data} ya está registrado.", "danger")
                return render_template('empleados/agregarEmpleados.html', form=form)

            try:
                pass_hash = generate_password_hash(form.password.data)
                nuevo_usuario = Usuario(
                    username=form.email.data,
                    email=form.email.data,
                    password_hash=pass_hash,
                    rol='ADMIN',
                    activo=True
                )
                db.session.add(nuevo_usuario)
                db.session.flush()

                img_b64 = request.form.get('imagen_base64_recuperada')
                if not img_b64:
                    archivo = request.files.get('imagen_empleado')
                    img_b64 = procesar_imagen_base64(archivo)

                nuevo_empleado = Empleado(
                    usuario_id=nuevo_usuario.id_usuario,
                    nombre=form.nombre.data,
                    apellido=form.apellido.data,
                    dni_cedula=form.dni_cedula.data,
                    email=form.email.data,
                    telefono=form.telefono.data,
                    direccion=form.direccion.data,
                    puesto=form.puesto.data,
                    salario_mensual=form.salario_mensual.data,
                    fecha_contratacion=form.fecha_contratacion.data,
                    imagen_empleado=img_b64,
                    estatus='ACTIVO'
                )
                
                db.session.add(nuevo_empleado)
                db.session.commit()
                
                flash("Empleado registrado con éxito", "success")
                return redirect(url_for('empleado.empleadosAdmin'))

            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "danger")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field.capitalize()}: {error}", "danger")
            
    return render_template('empleados/agregarEmpleados.html', form=form)

@empleado.route("/empleados/modificar/<int:id>", methods=["GET", "POST"])
def modificar_empleado(id):
    empleado_obj = Empleado.query.get_or_404(id)
    form = EmpleadoForm(obj=empleado_obj)
    
    if request.method == "POST":
        try:
            archivo = request.files.get('imagen_empleado')
            if archivo and archivo.filename != '':
                empleado_obj.imagen_empleado = procesar_imagen_base64(archivo)
            
            empleado_obj.nombre = request.form.get('nombre')
            empleado_obj.email = request.form.get('email')
            empleado_obj.telefono = request.form.get('telefono')
            empleado_obj.dni_cedula = request.form.get('dni_cedula')
            empleado_obj.puesto = request.form.get('puesto')
            empleado_obj.salario_mensual = request.form.get('salario_mensual')
            empleado_obj.direccion = request.form.get('direccion')
            empleado_obj.estatus = request.form.get('estatus')
            
            fecha_raw = request.form.get('fecha_contratacion')
            if fecha_raw:
                empleado_obj.fecha_contratacion = datetime.strptime(fecha_raw, '%Y-%m-%d')

            db.session.commit()
            flash("Empleado actualizado con exito", "success")
            return redirect(url_for("empleado.empleadosAdmin"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")

    fecha_string = empleado_obj.fecha_contratacion.strftime('%Y-%m-%d') if empleado_obj.fecha_contratacion else ""
    return render_template("empleados/modificarEmpleados.html", form=form, empleado=empleado_obj, empleado_id=id, fecha_string=fecha_string)

@empleado.route("/empleados/eliminar/<int:id>")
def eliminar_empleado(id):
    empleado_obj = Empleado.query.get_or_404(id)
    try:
        empleado_obj.estatus = 'INACTIVO'
        db.session.commit()
        flash("Empleado desactivado", "success")
    except Exception:
        db.session.rollback()
        flash("Error al desactivar", "danger")
    return redirect(url_for("empleado.empleadosAdmin"))

@empleado.route("/empleados/detalle/<int:id>")
def detalle_empleado(id):
    empleado_obj = Empleado.query.get_or_404(id)
    return render_template("empleados/detallesEmpleados.html", empleado=empleado_obj)