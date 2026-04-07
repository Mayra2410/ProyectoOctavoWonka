from flask import render_template, request, redirect, url_for, flash, session
from . import cliente 
from models import db, Cliente, Usuario
from .formsC import ClienteForm
from sqlalchemy import or_
import base64

@cliente.route('/clientes', methods=['GET'])
def clientesAdmin(): 
    search_query = request.args.get('q', '').strip()
    query = Cliente.query

    if search_query:
        filtros = [
            Cliente.nombre.ilike(f"%{search_query}%"),
            Cliente.email.ilike(f"%{search_query}%")
        ]
        query = query.filter(or_(*filtros))

    return render_template("clientes/clientesAdmin.html", 
                         form=ClienteForm(), 
                         clientes=query.all(), 
                         query=search_query)

@cliente.route("/clientes/agregar", methods=["GET", "POST"])
def agregar_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        archivo = request.files.get('imagen_cliente')
        imagen_recuperada = request.form.get('imagen_base64_recuperada')
        
        base64_final = None
        if archivo and archivo.filename != '':
            contenido = archivo.read()
            encoded = base64.b64encode(contenido).decode('utf-8')
            base64_final = f"data:{archivo.content_type};base64,{encoded}"
        elif imagen_recuperada and imagen_recuperada.startswith('data:image'):
            base64_final = imagen_recuperada

        if not base64_final:
            form.imagen_cliente.errors.append("La fotografia es obligatoria.")
        else:
            try:
                nuevo = Cliente(
                    nombre=form.nombre.data,
                    email=form.email.data,
                    telefono=form.telefono.data,
                    direccion=form.direccion.data,
                    tipo=form.tipo.data, 
                    categoria_comprador=form.categoria_comprador.data, 
                    imagen_cliente=base64_final,
                    notas=form.notas.data,
                    fecha_registro=form.fecha_registro.data
                )
                db.session.add(nuevo)
                db.session.commit()
                return redirect(url_for("cliente.clientesAdmin"))
            except Exception as e:
                db.session.rollback()
                if "Duplicate entry" in str(e) and "email" in str(e):
                    form.email.errors.append("Este correo electrónico ya está registrado en Wonka.")
                else:
                # Si es otro tipo de error, puedes dejar el flash o enviarlo a otro campo
                    flash(f"Error inesperado: {str(e)}", "danger")
    return render_template("clientes/agregarClientes.html", form=form)

@cliente.route("/clientes/modificar/<int:id>", methods=["GET", "POST"])
def modificar_cliente(id):
    cliente_obj = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente_obj)

    if form.validate_on_submit():
        duplicado = Cliente.query.filter(Cliente.email == form.email.data, Cliente.id_cliente != id).first()
        if duplicado:
            form.email.errors.append("Este correo ya esta registrado.")
        else:
            try:
                archivo = request.files.get('imagen_cliente')
                if archivo and archivo.filename != '':
                    encoded_string = base64.b64encode(archivo.read()).decode('utf-8')
                    cliente_obj.imagen_cliente = f"data:{archivo.content_type};base64,{encoded_string}"
                
                form.populate_obj(cliente_obj)
                db.session.commit()
                # flash("Cliente actualizado con exito", "success")
                return redirect(url_for("cliente.clientesAdmin"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", "danger")

    return render_template("clientes/modificarClientes.html", form=form, cliente_id=id, cliente=cliente_obj)
# 1. Ruta para MOSTRAR la confirmación
@cliente.route("/clientes/eliminar/<int:id>")
def eliminar_cliente(id):
    cliente_obj = Cliente.query.get_or_404(id)
    # Simplemente enviamos al nuevo HTML
    return render_template("clientes/eliminarCliente.html", cliente=cliente_obj)

# 2. Ruta para PROCESAR la desactivación (POST)
@cliente.route("/clientes/desactivar/<int:id>", methods=["POST"])
def desactivar_confirmado(id):
    cliente_obj = Cliente.query.get_or_404(id)
    try:
        cliente_obj.estatus = 'INACTIVO'
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error al desactivar: {str(e)}", "danger")
    
    return redirect(url_for("cliente.clientesAdmin"))

@cliente.route("/clientes/<int:id>")
def detalle_cliente(id):
    return render_template("clientes/detallesClientes.html", cliente=Cliente.query.get_or_404(id))

@cliente.route('/mi-perfil')
def detalles_cliente_vista():
    if 'user_id' not in session: return redirect(url_for('index'))
    
    # Buscamos el cliente asociado al usuario logueado
    obj_cliente = Cliente.query.filter_by(usuario_id=session['user_id']).first()
    return render_template('clientes/detallesClienteVistaCliente.html', cliente=obj_cliente)

@cliente.route('/mi-perfil/editar', methods=['GET', 'POST'])
def modificar_cliente_vista():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    obj_cliente = Cliente.query.filter_by(usuario_id=session['user_id']).first()
    
    if not obj_cliente:
        flash("No se encontró el perfil del cliente.", "danger")
        return redirect(url_for('index'))
        
    form = ClienteForm(obj=obj_cliente)

    if form.validate_on_submit():
        # Verificar si el nuevo correo ya lo tiene OTRO usuario para evitar errores
        nuevo_email = form.email.data
        usuario_duplicado = Usuario.query.filter(Usuario.email == nuevo_email, Usuario.id_usuario != session['user_id']).first()
        
        if usuario_duplicado:
            form.email.errors.append("Este correo ya está en uso por otra cuenta.")
            return render_template('clientes/modificarClienteVistaCliente.html', form=form, cliente=obj_cliente)

        try:
            # 1. Actualizar la tabla de CLIENTE
            form.populate_obj(obj_cliente)
            
            # 2. Actualizar la tabla de USUARIO (La del Login)
            # Buscamos el registro en la tabla Usuario usando el ID de la sesión
            user_login = Usuario.query.get(session['user_id'])
            if user_login:
                user_login.email = nuevo_email
                # También actualizamos el username si quieres que cambie en el header
                user_login.username = form.nombre.data 
            
            # 3. Manejo de imagen
            archivo = request.files.get('imagen_cliente')
            if archivo and archivo.filename != '':
                contenido = archivo.read()
                encoded = base64.b64encode(contenido).decode('utf-8')
                obj_cliente.imagen_cliente = f"data:{archivo.content_type};base64,{encoded}"
            
            db.session.commit()
            
            # 4. Actualizar la sesión para que el Header muestre el nombre nuevo de inmediato
            session['nombre'] = form.nombre.data
            
            flash("¡Datos actualizados! Ya puedes usar tu nuevo correo para entrar.", "success")
            return redirect(url_for('cliente.detalles_cliente_vista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al sincronizar datos: {str(e)}", "danger")
    
    return render_template('clientes/modificarClienteVistaCliente.html', form=form, cliente=obj_cliente)