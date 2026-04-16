from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash
from flask_mail import Message
import random
from models import db, Usuario
from .formsRC import RecuperarPassForm
from . import recuperarContrasenia 

@recuperarContrasenia.route("/recuperar", methods=["GET", "POST"])
def recuperar_password():
    from app import mail 
    form = RecuperarPassForm()
    
    if form.validate_on_submit():
        email = form.email.data
        nueva_pass = form.password.data
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user:
            codigo = random.randint(100000, 999999)
            user.codigo_verificacion = codigo
            user.password_hash = generate_password_hash(nueva_pass)
            user.verificado = False 
            db.session.commit()

            msg = Message("Seguridad Wonka: Restablecer Contrasena", recipients=[email])
            msg.body = f"Tu codigo de seguridad para el cambio de contrasena es: {codigo}"
            mail.send(msg)
            
            flash("Hemos enviado un codigo a tu correo para autorizar el cambio.", "info")
            return redirect(url_for('recuperarContrasenia.verificar_recuperacion', email=email))
        else:
            flash("El correo electronico no pertenece a ningun ciudadano de la fabrica.", "error")
            
    return render_template("recuperarContrasenia/recuperar.html", form=form)

@recuperarContrasenia.route("/verificar_recuperacion/<email>", methods=["GET", "POST"])
def verificar_recuperacion(email):
    if request.method == "POST":
        codigo_ingresado = request.form.get("codigo")
        user = Usuario.query.filter_by(email=email).first()

        if user and str(user.codigo_verificacion) == str(codigo_ingresado):
            user.verificado = True 
            user.codigo_verificacion = None 
            db.session.commit()

            flash("Tu contrasena se ha actualizado correctamente.", "success")
            return redirect(url_for('index'))
        else:
            flash("Codigo incorrecto.", "error")
            return redirect(url_for('recuperarContrasenia.verificar_recuperacion', email=email))

    return render_template("recuperarContrasenia/verificar_RC.html", email=email)