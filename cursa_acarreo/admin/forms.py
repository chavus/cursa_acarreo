from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, ValidationError, PasswordField, StringField
from wtforms.validators import Email, DataRequired, Optional
import cursa_acarreo.models.general as g
import cursa_acarreo.models.trip as t
import cursa_acarreo.models.user as u


from markupsafe import Markup, escape
from wtforms.widgets.core import html_params
from wtforms.compat import text_type

class CustomSelect(object):
    """
    ADDED TO DEFINE SELECT PLACE HOLDER AND DISABLE PLACEHOLDER
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        choices = [('default', 'Seleccionar...', True)]
        choices.extend([(val, label, selected) for val, label, selected in field.iter_choices()])
        for val, label, selected in choices:
            html.append(self.render_option(val, label, selected))
        html.append('</select>')
        return Markup(''.join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        if value is True:
            # Handle the special case of a 'True' value.
            value = text_type(value)

        options = dict(kwargs, value=value)
        if selected:
            options['selected'] = True
        if value == 'default':
            options['disabled'] = True
        if value == 'section_label':
            options['disabled'] = True
        return Markup('<option %s>%s</option>' % (html_params(**options), escape(label)))


class UserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired('Favor de ingresar un Nombre de Usuario')])
    name = StringField('Nombre')
    last_name = StringField('Apellido(s)')
    email = StringField('E-mail', validators=[Optional(), Email('Ingrese formato de Email válido')])
    role = SelectField('Rol', widget=CustomSelect(),
                       choices=[('admin', 'Admin'), ('supervisor', 'Supervisor'), ('operator', 'Checador')],
                       validators=[DataRequired('Favor de seleccionar un Rol')])
    password = PasswordField('Contraseña')
    password_confirm = PasswordField('Confirmar Contraseña')

    def __init__(self, user=None, **kwargs): # Had to do this to be able to validate duplicates when updating
        super(UserForm, self).__init__(**kwargs)
        self.user = user

    def validate_username(self, field):
        if u.User.find_by('username', field.data):
            if self.user:
                if not self.user.username == field.data:
                    raise ValidationError('Nombre de usuario ya existe')
            else:
                raise ValidationError('Nombre de usuario ya existe')

    def validate_email(self, field):
        if u.User.find_by('email', field.data):
            if self.user:
                if not self.user.email == field.data:
                    raise ValidationError('Email ya ha sido registrado')
            else:
                raise ValidationError('Email ya ha sido registrado')


    def validate_password(self, field):
        if not self.user:  # If new user, make password required
            if field.data == '':
                raise ValidationError('Favor de ingresar contraseña')
            elif field.data != self.password_confirm.data:
                raise ValidationError('Contraseñas no coinciden')
        else:  # If editing a user and password was entered, make sure password is confirmed
            if field.data != '' and field.data != self.password_confirm.data:
                    raise ValidationError('Contraseñas no coinciden')
