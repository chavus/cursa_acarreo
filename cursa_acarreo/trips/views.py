from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
import cursa_acarreo.trips.forms as f
from cursa_acarreo.models.trip import Trip
from importlib import reload

trips_blueprint = Blueprint('trips', __name__)


@trips_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    reload(f)
    form = f.CreateTripForm()
    available_trucks= f.get_available_trucks()
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
    return render_template('receive_home.html', in_progress_trips=in_progress_trips)

@trips_blueprint.route('/receive/<int:trip_id>')
@login_required
def receive(trip_id):
    trip = Trip.find_by_tripid(trip_id)
    trip.finalize(current_user.username, 'complete')
    flash('Viaje #{} ha sido completado'.format(trip_id))
    return redirect(url_for('trips.receive_dashboard'))


@trips_blueprint.route('/list')
@login_required
def list():
    trips = Trip.get_all()
    in_progress_trips = [i for i in trips if i['status'] == 'in_progress']
    finalized_trips = [i for i in trips if i['status'] in ['complete', 'canceled']]
    return render_template('list_home.html', in_progress_trips=in_progress_trips, finalized_trips=finalized_trips)

