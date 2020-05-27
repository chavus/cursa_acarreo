from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, ValidationError
import cursa_acarreo.models.general as g
import cursa_acarreo.models.trip as t

from markupsafe import Markup, escape
from wtforms.widgets.core import html_params
from wtforms.compat import text_type


def get_available_trucks():
    return [truck_ for truck_ in g.Truck.get_list_by('id_code') if truck_ not in t.Trip.get_trucks_in_trip()]


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
        return Markup('<option %s>%s</option>' % (html_params(**options), escape(label)))


def selection_required(form, field):
    if field.data == None:
        raise ValidationError('Favor de seleccionar una opción')


class CreateTripForm(FlaskForm):
    truck = SelectField('Camión', widget=CustomSelect(), validators=[selection_required], validate_choice=False)
    origin = SelectField('Origen',
                         choices=[(i, i) for i in (g.MaterialBank.get_list_by('name') + g.Project.get_list_by('name'))],
                         widget=CustomSelect(),
                         validators=[selection_required], validate_choice=False)
    material = SelectField('Material',
                           choices=[(i, i) for i in g.Material.get_list_by('name')], widget=CustomSelect(),
                           validators=[selection_required], validate_choice=False)
    destination = SelectField('Destino',
                              choices=[(i, i) for i in (g.MaterialBank.get_list_by('name') + g.Project.get_list_by('name'))],
                              widget=CustomSelect(),
                              validators=[selection_required], validate_choice=False)

    submit = SubmitField('Confirmar Viaje')








