import datetime

from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from ..utils import utils
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
    form.customer.choices = f.customers_choice()
    return render_template('create_home.html', form=form)


@trips_blueprint.route('/create_trip', methods=['POST'])
@login_required
def create_trip():
    trip_dict = {
        'type': request.form.get('trip_type'),
        'truck_id': request.form.get('truck_id'),
        'amount': int(request.form.get('amount')) if request.form.get('amount') else None,
        'material_name': request.form.get('material_name'),
        'origin_name': request.form.get('origin_name'),
        'destination_name': request.form.get('destination_name'),
        'client_name': request.form.get('customer_name'),
        'sender_username': current_user.username,
        'sender_comment': request.form.get('sender_comment'),
        'status': 'in_progress' if request.form.get('trip_type') == "internal" else "complete"
    }
    try:
        trip = Trip.create(**trip_dict)
        return jsonify({'trip_id': trip.trip_id}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 400


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
        return jsonify(error=str(e)), 400


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



@trips_blueprint.route('/_get_distinct_values')
@login_required
def get_distinct_values():
    field = request.args.get('field')
    values = Trip.get_distinct_values(field)
    dict_of_values = {v: v for v in values}
    return json.dumps(dict_of_values)


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
        distance = request.json['distance']
        finalizer_comment = request.json['finalizer_comment']
        if finalizer_comment is None:
            finalizer_comment = ""
        trip = Trip.find_by_tripid(trip_id)
        if current_user.role not in ["supervisor", "admin"] and trip.sender_user == current_user.username:
            return jsonify(
                error=f'Viaje no puede ser creado y recibido por mismo usuario: {current_user.username}!'), 403

        if trip.status == 'in_progress':
            trip.finalize(current_user.username, status, distance, finalizer_comment)
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


@trips_blueprint.route('/delete_trip', methods=['POST'])
@login_required
@mustbe_admin
def delete():
    try:
        trip_id = request.json['trip_id']
        trip = Trip.find_by_tripid(trip_id)
        trip.delete()
        return jsonify(f'Viaje: #{trip_id} fue eliminado.')
    except Exception as e:
        return jsonify(f'Error: {e}'), 500


@trips_blueprint.route('/list')
@mustbe_admin
@login_required
def list():
    in_progress_trips = Trip.get_formatted_trips(status=['in_progress'])
    return render_template('list_home_cs_pagination.html', in_progress_trips=in_progress_trips)

# FOR DEVELOPMENT:
# @trips_blueprint.route('/in-progress-trips-ss')
# @mustbe_admin
# @login_required
# def in_progress_trips_ss():
#     # offset: where it starts from 0
#     # limit: how many
#     # 1. filters
#     # 2. exports
#     # 3. search
#     # 4. spinner
#     # 5. delete button
#
#     print(request.args)
#     offset = int(request.args.get('offset'))
#     limit = int(request.args.get('limit'))
#     print(offset, limit)
#     trips = Trip.get_all()
#     finalized_trips = sorted([i for i in trips if i['status'] in ['complete', 'canceled']],
#                              key=lambda i: i['trip_id'], reverse=True)
#     sliced_trips_list = finalized_trips[offset:offset + limit]
#     paginated_dict_payload = {'total': len(finalized_trips),
#                               'rows': sliced_trips_list}
#     return jsonify(paginated_dict_payload)


@trips_blueprint.route('/completed-trips-cs')
@mustbe_admin
@login_required
def completed_trips_cs():
    finalized_trips = Trip.get_formatted_trips(status=['complete', 'canceled'], purpose='table')
    response = jsonify(finalized_trips)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@trips_blueprint.route('/trips-csv')
@mustbe_admin
def trips_csv():
    trips_list = Trip.get_formatted_trips(purpose='csv')
    fields = ['#', 'Tipo', 'Estado', 'Camión', 'Chofer', 'Material', 'mts3', 'Origen', 'Destino', 'Kms', 'Cliente',
              'Envió', 'Fecha/Hora Envío', 'Comentario Envío', 'Finalizó', 'Fecha/Hora Finalizado', 'Comentario Recibo']
    export_name_date_append = utils.formatdate_mx(datetime.datetime.utcnow())
    return utils.send_csv(trips_list,
                          f'acarreos_{export_name_date_append}.csv', fields)
