from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
import cursa_acarreo.trips.forms as f
from cursa_acarreo.models.trip import Trip
from importlib import reload
import datetime
from cursa_acarreo.security import mustbe_admin

trips_blueprint = Blueprint('trips', __name__)


@trips_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    reload(f)
    form = f.CreateTripForm()
    available_trucks = f.get_available_trucks()
    if form.validate_on_submit():
        trip_dict = {
            'truck_id': form.truck.data,
            'material_name': form.material.data,
            'project_name': form.project.data,
            'origin_name': form.origin.data,
            'sender_username': current_user.username
        }
        trip = Trip.create(**trip_dict)
        flash('Viaje #{} creado!'.format(trip.trip_id))
        return redirect(url_for('trips.create'))
    return render_template('create_home.html', form=form, available_trucks=available_trucks)


@trips_blueprint.route('/receive_dashboard')
@login_required
def receive_dashboard():
    trips = Trip.get_all()
    in_progress_trips = [i for i in trips if i['status'] == 'in_progress']
    # in_progress_trips = [{'trip_id': 23, 'truck': 'T005', 'material': 'Asfalto', 'amount': 15, 'project': 'Calle X', 'origin': 'Mina', 'sender_user': 'sjimenez', 'sent_datetime': datetime.datetime(2020, 5, 12, 18, 35, 1, 422000), 'finalizer_user': None, 'finalized_datetime': None, 'status': 'in_progress'}, {'trip_id': 24, 'truck': 'T002', 'material': 'Grava', 'amount': 13, 'project': 'Libramiento Tecoman', 'origin': 'Mina', 'sender_user': 'sjimenez', 'sent_datetime': datetime.datetime(2020, 5, 12, 18, 35, 1, 422000), 'finalizer_user': None, 'finalized_datetime': None, 'status': 'in_progress'}, {'trip_id': 25, 'truck': 'T001', 'material': 'Grava', 'amount': 14, 'project': 'Libramiento Tecoman', 'origin': 'Mina', 'sender_user': 'sjimenez', 'sent_datetime': datetime.datetime(2020, 5, 12, 18, 35, 1, 422000), 'finalizer_user': None, 'finalized_datetime': None, 'status': 'in_progress'}, {'trip_id': 26, 'truck': 'T003', 'material': 'Grava', 'amount': 15, 'project': 'Libramiento Tecoman', 'origin': 'Mina', 'sender_user': 'user1', 'sent_datetime': datetime.datetime(2020, 5, 12, 1, 12, 4, 212000), 'finalizer_user': None, 'finalized_datetime': None, 'status': 'in_progress'}]

    return render_template('receive_home.html', in_progress_trips=in_progress_trips)

@trips_blueprint.route('/receive/<int:trip_id>')
@login_required
def receive(trip_id):
    trip = Trip.find_by_tripid(trip_id)
    trip.finalize(current_user.username, 'complete')
    flash('Viaje #{} ha sido completado'.format(trip_id))
    return redirect(url_for('trips.receive_dashboard'))


@trips_blueprint.route('/list')
@mustbe_admin
@login_required
def list():
    # trips = Trip.get_all()
    # in_progress_trips = [i for i in trips if i['status'] == 'in_progress']
    # finalized_trips = [i for i in trips if i['status'] in ['complete', 'canceled']]
    in_progress_trips = [{'trip_id': 3, 'truck': 'T003', 'material': 'Arena', 'amount': 15, 'project': 'Carretera a Colima', 'origin': 'Rio', 'destination': 'Carretera', 'sender_user': 'user1', 'sent_datetime': datetime.datetime(2020, 5, 4, 0, 8, 22, 822000), 'finalizer_user': None, 'finalized_datetime': None, 'status': 'in_progress'}, {'trip_id': 5, 'truck': 'T005', 'material': 'Arena', 'amount': 15, 'project': 'Libramiento Tecoman', 'origin': 'Mina', 'destination': 'Carretera', 'sender_user': 'user1', 'sent_datetime': datetime.datetime(2020, 5, 4, 0, 8, 22, 822000), 'finalizer_user': None, 'finalized_datetime': None, 'status': 'in_progress'}]
    finalized_trips = [{'trip_id': 2, 'truck': 'T001', 'material': 'Grava', 'amount': 14, 'project': 'Libramiento Tecoman', 'origin': 'Mina', 'destination': 'Libramiento', 'sender_user': 'user1', 'sent_datetime': datetime.datetime(2020, 5, 4, 0, 8, 22, 822000), 'finalizer_user': 'sjimenez', 'finalized_datetime': datetime.datetime(2020, 5, 4, 0, 32, 50, 769000), 'status': 'complete'}, {'trip_id': 4, 'truck': 'T004', 'material': 'Asfalto', 'amount': 17, 'project': 'Calle X', 'origin': 'Planta Asfalto', 'destination': 'Calle Manzanillo', 'sender_user': 'user1', 'sent_datetime': datetime.datetime(2020, 5, 4, 0, 8, 22, 822000), 'finalizer_user': 'sjimenez', 'finalized_datetime': datetime.datetime(2020, 5, 4, 0, 33, 41, 821000), 'status': 'complete'}, {'trip_id': 6, 'truck': 'T004', 'material': 'Arena', 'amount': 17, 'project': 'Calle X', 'origin': 'Rio', 'destination': 'Libramiento', 'sender_user': 'user1', 'sent_datetime': datetime.datetime(2020, 5, 4, 0, 8, 22, 822000), 'finalizer_user': 'dsoto', 'finalized_datetime': datetime.datetime(2020, 5, 4, 0, 34, 28, 883000), 'status': 'canceled'}]
    return render_template('list_home.html', in_progress_trips=in_progress_trips, finalized_trips=finalized_trips)

