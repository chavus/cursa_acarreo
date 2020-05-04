from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
import cursa_acarreo.models.general as g


class CreateTripForm(FlaskForm):
    truck = SelectField('Camion', choices=[(i, i) for i in g.Truck.get_list_by('id_code')])
    material = SelectField('Material', choices=[(i, i) for i in g.Material.get_list_by('name')])
    project = SelectField('Obra', choices=[(i, i) for i in g.Project.get_list_by('name')])
    origin = SelectField('Banco', choices=[(i, i) for i in g.Origin.get_list_by('name')])
    destination = SelectField('Destino', choices=[(i, i) for i in g.Destination.get_list_by('name')])
    submit = SubmitField('Crear')
