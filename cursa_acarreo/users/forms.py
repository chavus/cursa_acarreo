from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
from wtforms import ValidationError
from cursa_acarreo.models.user import User


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[InputRequired('Este campo es requerido')])
    password = PasswordField('Contraseña', validators=[InputRequired('Este campo es requerido')])
    submit = SubmitField('Ingresar')

    def validate_username(self, username):
        if not User.find_by_username(username.data, False):
            raise ValidationError('Usuario "{}" no encontrado'.format(username.data))
