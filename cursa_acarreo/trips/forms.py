from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, ValidationError, TextAreaField, validators
import cursa_acarreo.models.general as g
import cursa_acarreo.models.trip as t

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


def selection_required(form, field):
    if field.data is None:
        raise ValidationError('Favor de seleccionar una opción')


def _available_trucks():
    active_trucks = g.Truck.get_active()
    trucks_in_trip = t.Trip.get_trucks_in_trip()
    return list(filter(lambda truck: truck not in trucks_in_trip, active_trucks))
    # return [truck_ for truck_ in g.Truck.get_active() if truck_ not in t.Trip.get_trucks_in_trip()]


# Returns active and available trucks
def truck_choices():
    return [(i, i) for i in _available_trucks()]


def bank_choices():
    return [(i, i) for i in g.MaterialBank.get_active()]


def project_choices():
    return [(i, i) for i in g.Project.get_active()]


def material_choices():
    return [(i, i) for i in g.Material.get_list_by('name')]


def customers_choice():
    return [(i, i) for i in g.Customer.get_list_by('name')]


class CreateTripForm(FlaskForm):
    truck = SelectField('Camión', widget=CustomSelect(), validators=[selection_required], validate_choice=False)
    origin = SelectField('Origen',
                         widget=CustomSelect(),
                         validators=[selection_required], validate_choice=False)
    material = SelectField('Material',
                           widget=CustomSelect(),
                           validators=[selection_required], validate_choice=False)
    destination = SelectField('Destino',
                              widget=CustomSelect(),
                              validators=[selection_required], validate_choice=False)
    customer = SelectField('Cliente',
                           widget=CustomSelect(), validate_choice=False)
    sender_comment = TextAreaField('Agregar comentario:', validators=[validators.Length(max=t.Trip.sender_comment.max_length, message="Máximo 100 caracteres!")])

    submit = SubmitField('Crear Viaje')







