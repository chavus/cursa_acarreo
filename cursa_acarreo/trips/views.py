from flask import Blueprint, render_template, flash, request, jsonify
from flask_login import login_required, current_user
import cursa_acarreo.trips.forms as f
from cursa_acarreo.trips.ticket import Ticket
from cursa_acarreo.models.trip import Trip
from cursa_acarreo.models.general import MaterialBank, Project
from cursa_acarreo.security import mustbe_admin
import json


trips_blueprint = Blueprint('trips', __name__)

@trips_blueprint.route('/create_home')
@login_required
def create_home():
    form = f.CreateTripForm()
    form.truck.choices = f.truck_choices()
    form.origin.choices = [('section_label', '-------Bancos-------')] + f.bank_choices() + \
                          [('section_label', '-------Obras--------')] + f.project_choices()
    form.material.choices = f.material_choices()
    form.destination.choices = [('section_label', '-------Obras--------')] + f.project_choices() + \
                               [('section_label', '-------Bancos-------')] + f.bank_choices()
    return render_template('create_home.html', form=form)


@trips_blueprint.route('/create_trip', methods=['POST'])
@login_required
def create_trip():
    trip_dict = {
        'truck_id': request.form.get('truck_id'),
        'material_name': request.form.get('material_name'),
        'origin_name': request.form.get('origin_name'),
        'destination_name': request.form.get('destination_name'),
        'sender_username': current_user.username,
        'sender_comment': request.form.get('sender_comment')
        }
    try:
        trip = Trip.create(**trip_dict)
        return jsonify({'trip_id': trip.trip_id}), 200
    except Exception as e:
        return jsonify({'error': e.args[0]}), 400


@trips_blueprint.route('/get_trip_ticket')
@login_required
def get_trip_ticket():
    try:
        trip_id = request.args.get('trip_id')
        trip_dict = Trip.find_by_tripid(int(trip_id))
        ticket = Ticket(trip_dict)
        ticket.create_ticket()
        ticket_b64 = ticket.encode_b64()
        return jsonify(ticket_b64=ticket_b64.decode()), 200
    except Exception as e:
        return jsonify(error=e.args[0]), 400


@trips_blueprint.route('/_get_materials')
@login_required
def _get_materials():
    location = request.args.get('origin', '01', type=str)
    bank = MaterialBank.find_by_name(location, False)
    project = Project.find_by_name(location, False)
    if bank:
        materials = bank.get_list_of_materials()
    elif project:
        materials = project.get_list_of_materials()
    else:
        materials = []
    material_choices = [(m, m) for m in materials]
    return jsonify(material_choices)

@trips_blueprint.route('/_get_materials_on_trip')
@login_required
def _get_materials_on_trip():
    trips = Trip.get_all()
    materials_in_progress_l = set([i['material'] for i in trips])
    dict_of_materials = {m: m for m in materials_in_progress_l}
    return json.dumps(dict_of_materials)


@trips_blueprint.route('/receive_dashboard')
@login_required
def receive_dashboard():
    trips = Trip.get_all()
    in_progress_trips = [i for i in trips if i['status'] == 'in_progress']
    return render_template('receive_home.html', in_progress_trips=in_progress_trips)


@trips_blueprint.route('/_get_trip_info')
@login_required
def get_trip_info():
    try:
        print(request.args.get('trip_id'))
        trip_id = request.args.get('trip_id')
        trip = Trip.find_by_tripid(trip_id)
        return trip.to_json(), 200
    except Exception as e:
        print(e)
        return jsonify(error=f'Server Error: {e.args[0]}'), 500


@trips_blueprint.route('/receive', methods=['POST'])
@login_required
def receive():
    try:
        trip_id = request.json['trip_id']
        status = request.json['status']
        finalizer_comment = request.json['finalizer_comment']
        if finalizer_comment is None:
            finalizer_comment = ""
        trip = Trip.find_by_tripid(trip_id)
        if trip.status == 'in_progress':
            trip.finalize(current_user.username, status, finalizer_comment)
            if status == 'complete':
                return jsonify(message=f'Viaje #{trip_id} con camión {trip.truck} ha sido RECIBIDO!'), 200
            elif status == 'canceled':
                return jsonify(message=f'Viaje #{trip_id} con camión {trip.truck} ha sido CANCELADO!'), 200
        else:
            status_translation = {'complete': 'COMPLETO', 'canceled': 'CANCELADO'}
            return jsonify(message=f'Viaje #{trip_id} con camión {trip.truck} ya había sido completado con estatus: \
                                    {status_translation[trip.status]}!'), 409
    except Exception as e:
        print(e)
        return jsonify(error=f'Server Error: {e.args[0]}'), 500


@trips_blueprint.route('/list')
@mustbe_admin
@login_required
def list():
    trips = Trip.get_all()
    in_progress_trips = [i for i in trips if i['status'] == 'in_progress']
    finalized_trips = sorted([i for i in trips if i['status'] in ['complete', 'canceled']],
                             key=lambda i: i['trip_id'], reverse=True)
    return render_template('list_home.html', in_progress_trips=in_progress_trips, finalized_trips=finalized_trips)
