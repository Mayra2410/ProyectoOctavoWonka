from functools import wraps
from flask import session, flash, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"DEBUG: Intentando acceder a ruta. Session actual: {session}") 
        if 'user_id' not in session:
            print("DEBUG: No hay user_id. Redirigiendo al login...")
            flash("Debes iniciar sesión para acceder al sistema.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

from flask import make_response