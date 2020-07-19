from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify, send_from_directory
from flask_login import login_required, current_user
import cursa_acarreo.trips.forms as f
from cursa_acarreo.models.trip import Trip
from cursa_acarreo.models.general import MaterialBank, Project
from cursa_acarreo.security import mustbe_admin
import json

trips_blueprint = Blueprint('trips', __name__)


@trips_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = f.CreateTripForm()
    form.truck.choices = f.truck_choices()
    form.origin.choices = [('section_label', '-------Bancos-------')] + f.bank_choices() + \
                          [('section_label', '-------Obras--------')] + f.project_choices()
    form.material.choices = f.material_choices()
    form.destination.choices = [('section_label', '-------Obras--------')] + f.project_choices() + \
                            [('section_label', '-------Bancos-------')] + f.bank_choices()
    if form.validate_on_submit():
        trip_dict = {
            'truck_id': form.truck.data,
            'material_name': form.material.data,
            'origin_name': form.origin.data,
            'destination_name': form.destination.data,
            'sender_username': current_user.username,
            'sender_comment': form.sender_comment.data
        }
        print('sender_comment: ', trip_dict['sender_comment'])
        trip = Trip.create(**trip_dict)
        flash('Viaje #{} con camión {} creado!'.format(trip.trip_id, trip.truck),
              ('success', 'popup'))
        return redirect(url_for('trips.create'))
    return render_template('create_home.html', form=form)


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


@trips_blueprint.route('/receive', methods=['POST'])
@login_required
def receive():
    try:
        trip_id = request.form.get('trip_id')
        status = request.form.get('status')
        finalizer_comment = request.form.get('finalizer_comment')
        if finalizer_comment is None:
            finalizer_comment = ""
        print('finalizer_comment: ', finalizer_comment)
        trip = Trip.find_by_tripid(trip_id)
        trip.finalize(current_user.username, status, finalizer_comment)
        if status == 'complete':
            flash('Viaje #{} con camión {} ha sido recibido!'.format(trip_id, trip.truck),
                  ('success', 'popup'))
        elif status == 'canceled':
            flash('Viaje #{} con camión {} ha sido cancelado!'.format(trip_id, trip.truck),
                  ('success', 'popup'))
        return jsonify('success')
    except Exception as e:
        return jsonify(e.args[0])


@trips_blueprint.route('/list')
@mustbe_admin
@login_required
def list():
    trips = Trip.get_all()
    in_progress_trips = [i for i in trips if i['status'] == 'in_progress']
    finalized_trips = sorted([i for i in trips if i['status'] in ['complete', 'canceled']],
                             key=lambda i: i['trip_id'], reverse=True)
    return render_template('list_home.html', in_progress_trips=in_progress_trips, finalized_trips=finalized_trips)

@trips_blueprint.route('/test.pdf')
def test_print():
    return send_from_directory('temp', 'test.pdf')

@trips_blueprint.route('/printbt') 
def test_printbt():
    return json.dumps( {'type': 0, 'content': "Printing!", 'bold': 1, 'align': 2, 'format': 0} )  