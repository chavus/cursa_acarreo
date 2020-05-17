from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, widgets
import cursa_acarreo.models.general as g
import cursa_acarreo.models.trip as t

from markupsafe import Markup, escape
from wtforms.widgets.core import html_params
from wtforms.compat import text_type


def get_available_trucks():
    return [truck.id_code for truck in g.Truck.objects
            if truck not in [trip.truck for trip in t.Trip.objects(status="in_progress")]]


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
        print('iter', [(val, label, selected) for val, label, selected in field.iter_choices()])
        choices.extend([(val, label, selected) for val, label, selected in field.iter_choices()])
        print(choices)
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

# def custom_option(value, label, selected, **kwargs):
#     if value is True:
#         # Handle the special case of a 'True' value.
#         value = text_type(value)
#
#     options = dict(kwargs, value=value)
#     if selected:
#         options['selected'] = True
#     return Markup('<option %s>%s</option>' % (html_params(**options), escape(label)))


class CreateTripForm(FlaskForm):
    # truck = SelectField('Camión', choices=[(i, i) for i in get_available_trucks()])   Current option
    truck = SelectField('Camión', widget=CustomSelect())

    # truck = SelectField('Camión', choices=[(0, 'T002'), (1, 'T003'), (2, 'T004'), (3, 'T005')], default=3)

    material = SelectField('Material', choices=[(i, i) for i in g.Material.get_list_by('name')], widget=CustomSelect())
    project = SelectField('Obra', choices=[(i, i) for i in g.Project.get_list_by('name')], widget=CustomSelect())
    origin = SelectField('Banco', choices=[(i, i) for i in g.Origin.get_list_by('name')], widget=CustomSelect())
    submit = SubmitField('Confirmar Viaje')







