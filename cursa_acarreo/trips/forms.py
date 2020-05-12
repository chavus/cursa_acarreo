from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
import cursa_acarreo.models.general as g
import cursa_acarreo.models.trip as t


def get_available_trucks():
    return [truck.id_code for truck in g.Truck.objects
            if truck not in [trip.truck for trip in t.Trip.objects(status="in_progress")]]


class CreateTripForm(FlaskForm):
    truck = SelectField('Camión', choices=[(i, i) for i in get_available_trucks()])
    material = SelectField('Material', choices=[(i, i) for i in g.Material.get_list_by('name')])
    project = SelectField('Obra', choices=[(i, i) for i in g.Project.get_list_by('name')])
    origin = SelectField('Banco', choices=[(i, i) for i in g.Origin.get_list_by('name')])
    # destination = SelectField('Destino', choices=[(i, i) for i in g.Destination.get_list_by('name')])
    submit = SubmitField('Confirmar Viaje')
