from flask_wtf import FlaskForm
from wtforms import (SelectField, SelectMultipleField, ValidationError, PasswordField, StringField, TextAreaField,
                     BooleanField, DecimalField, IntegerField)
# from wtforms.fields.html5 import DecimalField, IntegerField
from wtforms.validators import Email, DataRequired, Optional
import cursa_acarreo.models.general as g
import cursa_acarreo.models.trip as t
import cursa_acarreo.models.user as u


from markupsafe import Markup, escape
from wtforms.widgets.core import html_params
# from wtforms.compat import text_type

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
            value = str(value)

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
                       choices=[('operator', 'Checador'), ('creator', 'Altas'), ('supervisor', 'Supervisor'), ('admin', 'Admin')],
                       validators=[DataRequired('Favor de seleccionar un Rol')])
    password = PasswordField('Contraseña')
    password_confirm = PasswordField('Confirmar Contraseña')

    def __init__(self, user=None, **kwargs):  # Had to do this to be able to validate duplicates when updating
        super(UserForm, self).__init__(**kwargs)
        self.user = user

    def validate_username(self, field):
        if u.User.find_by('username', field.data.lower()):
            if self.user:
                if not self.user.username.lower() == field.data.lower():
                    raise ValidationError('Nombre de usuario ya existe')
            else:
                raise ValidationError('Nombre de usuario ya existe')

    def validate_email(self, field):
        if u.User.find_by('email', field.data.lower()):
            if self.user:
                if not ('' if not self.user.email else self.user.email.lower()) == field.data.lower():
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


class SupplierForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired('Favor de ingresar un Nombre de Proveedor')])

    def __init__(self, supplier=None, **kwargs):  # Had to do this to be able to validate duplicates when updating
        super(SupplierForm, self).__init__(**kwargs)
        self.supplier = supplier

    def validate_name(self, field):
        if g.Supplier.find_by_name(field.data, False):
            if self.supplier:
                if not self.supplier.name.lower() == field.data.lower():
                    raise ValidationError('Nombre de Proveedor ya existe')
            else:
                raise ValidationError('Nombre de Proveedor ya existe')


class CustomerForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired('Favor de ingresar un Nombre de Cliente')])

    def __init__(self, customer=None, **kwargs):  # Had to do this to be able to validate duplicates when updating
        super(CustomerForm, self).__init__(**kwargs)
        self.customer = customer

    def validate_name(self, field):
        if g.Customer.find_by_name(field.data, False):
            if self.customer:
                if not self.customer.name.lower() == field.data.lower():
                    raise ValidationError('Nombre de Cliente ya existe')
            else:
                raise ValidationError('Nombre de Cliente ya existe')


class MaterialForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired('Favor de ingresar un Nombre de Material')])
    description = TextAreaField('Descripción')

    def __init__(self, material=None, **kwargs):  # Had to do this to be able to validate duplicates when updating
        super(MaterialForm, self).__init__(**kwargs)
        self.material = material

    def validate_name(self, field):
        if g.Material.find_by_name(field.data, False):
            if self.material:
                if not self.material.name.lower() == field.data.lower():
                    raise ValidationError('Material ya existe')
            else:
                raise ValidationError('Material ya existe')

class BankForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired('Favor de ingresar un Nombre de Banco')])
    location = StringField('Ubicación')
    description = TextAreaField('Descripción')
    owner_name = SelectField('Propietario', validate_choice=False)  # Must mark as validate_choice=False to skip validation
    material_name_list = SelectMultipleField('Materiales disponibles')
    royalty = DecimalField('Royalty', validators=[Optional()])
    is_active = BooleanField('Activo', default='checked')

    def __init__(self, bank=None, **kwargs):  # Had to do this to be able to validate duplicates when updating
        super(BankForm, self).__init__(**kwargs)
        self.bank = bank

    def validate_name(self, field):
        if g.MaterialBank.find_by_name(field.data, False):
            if self.bank:
                if not self.bank.name.lower() == field.data.lower():
                    raise ValidationError('Banco ya existe')
            else:
                raise ValidationError('Banco ya existe')

    def validate_royalty(self, field):
        if field.data:
            if field.data < 0:
                raise ValidationError('Ingresa una cantidad igual o mayor a 0')


class ProjectForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired('Favor de ingresar un Nombre de Obra')])
    location = StringField('Ubicación')
    description = TextAreaField('Descripción')
    customer_name = SelectField('Cliente',
                                validate_choice=False)  # Must mark as validate_choice=False to skip validation
    material_name_list = SelectMultipleField('Materiales requeridos')
    resident = StringField('Residente')
    is_active = BooleanField('Activo', default='checked')

    def __init__(self, project=None, **kwargs):  # Had to do this to be able to validate duplicates when updating
        super(ProjectForm, self).__init__(**kwargs)
        self.project = project

    def validate_name(self, field):
        if g.Project.find_by_name(field.data, False):
            if self.project:
                if not self.project.name.lower() == field.data.lower():
                    raise ValidationError('Obra ya existe')
            else:
                raise ValidationError('Obra ya existe')


class DriverForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired('Favor de ingresar un Nombre')])
    last_name = StringField('Apellido(s)', validators=[DataRequired('Favor de ingresar Apellido(s)')])

    def __init__(self, driver=None, **kwargs):  # Had to do this to be able to validate duplicates when updating
        super(DriverForm, self).__init__(**kwargs)
        self.driver = driver

    def validate_name(self, field):
        if g.Driver.find_by_full_name(name=field.data, last_name=self.last_name.data, raise_if_none=False):
            if self.driver:
                if not (self.driver.name.lower() == field.data.lower() and
                        self.driver.last_name.lower() == self.last_name.data.lower()):
                    raise ValidationError('Combinación de Nombre y Apellido ya existe')
            else:
                raise ValidationError('Combinación de Nombre y Apellido ya existe')


class TruckForm(FlaskForm):
    id_code = StringField('Código', validators=[DataRequired('Favor de ingresar un Código de camión')])
    brand = StringField('Marca')
    color = StringField('Color')
    serial_number = StringField('Número de Serie', validators=[DataRequired('Favor de ingresar Número de Serie de camión')])
    plate = StringField('Placa')
    capacity = IntegerField('Capacidad', validators=[DataRequired('Favor de ingresar Capacidad de camión en numeros enteros.')])
    driver_full_name = SelectField('Chofer',
                                validate_choice=False)  # Must mark as validate_choice=False to skip validation
    owner_name = SelectField('Propietario',
                                validate_choice=False)  # Must mark as validate_choice=False to skip validation    resident = StringField('Residente')
    is_active = BooleanField('Activo', default='checked')

    def __init__(self, truck=None, **kwargs):  # Had to do this to be able to validate duplicates when updating
        super(TruckForm, self).__init__(**kwargs)
        self.truck = truck

    def validate_id_code(self, field):
        if g.Truck.find_by_idcode(field.data, False):
            if self.truck:
                if not self.truck.id_code.lower() == field.data.lower():
                    raise ValidationError('Código ya existe')
            else:
                raise ValidationError('Código ya existe')

    def validate_serial_number(self, field):
        if g.Truck.find_by('serial_number', field.data):
            if self.truck:
                if not self.truck.serial_number.lower() == field.data.lower():
                    raise ValidationError('Número de Serie ya existe')
            else:
                raise ValidationError('Número de Serie ya existe')

    def validate_plate(self, field):
        if field.data and g.Truck.find_by('plate', field.data):
            if self.truck:
                if not self.truck.plate.lower() == field.data.lower():
                    raise ValidationError('Número de Placa ya existe')
            else:
                raise ValidationError('Número de Placa ya existe')

    def validate_capacity(self, field):
        if field.data:
            if field.data < 0:
                raise ValidationError('Ingresa una cantidad igual o mayor a 0')
