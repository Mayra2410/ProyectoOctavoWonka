from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

class RecuperarPassForm(FlaskForm):
    email = StringField('Correo Electronico', validators=[DataRequired(), Email()])
    password = PasswordField('Nueva Contraseña', validators=[DataRequired()])