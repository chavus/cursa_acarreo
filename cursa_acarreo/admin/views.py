import sys

from flask import Blueprint, render_template, flash, request, url_for, redirect
from cursa_acarreo.admin import forms
from cursa_acarreo.models.user import User
from cursa_acarreo.models import general as g
from cursa_acarreo.models.trip import Trip
from cursa_acarreo.security import mustbe_admin, mustbe_admin_or_creator
from flask_login import login_user, current_user, login_required, logout_user

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')


@admin_blueprint.before_request
@login_required
@mustbe_admin_or_creator
def validate_login_admin():  # before_request executed to validate if user is logged in and admin
    if request.endpoint and current_user.role != 'admin':
        print('User is not an admin')
    else:
        print('Admin')


'''
PANEL
'''


@admin_blueprint.route('/general-admin')
@mustbe_admin
def general_admin():
    return render_template('admin_panel/general_admin.html')

@admin_blueprint.route('/trips-admin')
@mustbe_admin
def trips_admin():
    trips = Trip.get_all()
    in_progress_trips = [i for i in trips if i['status'] == 'in_progress']
    finalized_trips = sorted([i for i in trips if i['status'] in ['complete', 'canceled']],
                             key=lambda i: i['trip_id'], reverse=True)
    return render_template('admin_panel/trips_admin.html', in_progress_trips=in_progress_trips,
                           finalized_trips=finalized_trips)


@admin_blueprint.route('/trips-admin/delete/<id>', methods=['POST', 'GET'])
@mustbe_admin
def trip_delete(id):
    try:
        print("trying with id ", id)
        trip = Trip.find_by_tripid(id)
        trip.delete()
        flash(f'Viaje: {id} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.trips_admin'))


'''
CONFIGURACION
'''

'''
USERS
'''


@admin_blueprint.route('/admin-users')
@mustbe_admin
def admin_users():
    users = User.get_all()
    return render_template('admin_panel/users_admin.html', users=users)


@admin_blueprint.route('/admin-users/new', methods=['GET', 'POST'])
@admin_blueprint.route('/admin-users/edit/<username>', methods=['GET', 'POST'])
@mustbe_admin
def user_add_edit(username=None):
    if username:
        try:
            user = User.find_by_username(username)
            form = forms.UserForm(**user.json(), user=user)  # Create a form passing value of users for duplicate # validations
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.admin_users')
    else:
        form = forms.UserForm()

    if form.validate_on_submit():
        if not username:  # New user
            try:
                user_new = {}
                for f in form:
                    user_new[f.name] = f.data
                del user_new['csrf_token']
                del user_new['password_confirm']
                User.add(**user_new)
                flash(f"Usuario: {user_new['username'].lower()} fue agregado", ['success', 'popup'])
                return redirect(url_for('admin.admin_users'))
            except Exception as e:
                return render_template('admin_panel/error_pages/500.html', error=e, back_page='admin.admin_users')
        else:  # Editing existing user
            try:
                user_form = {}
                for f in form:
                    user_form[f.name] = f.data
                del user_form['csrf_token']
                del user_form['password_confirm']
                if user_form['password'] == '':
                    del user_form['password']
                user.update(**user_form)
                flash(f"Usuario: {username.lower()} fue actualizado.", ['success', 'popup'])
                return redirect(url_for('admin.admin_users'))
            except Exception as e:
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/user_add_edit.html', form=form, user=User,
                           action='edit' if username else 'create')


@admin_blueprint.route('/admin-users/delete/<username>', methods=['GET', 'POST'])
@mustbe_admin
def user_delete(username):
    try:
        user = User.find_by_username(username)
        user.delete()
        flash(f'Usuario: {username} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.admin_users'))


'''
SUPPLIERS
'''


@admin_blueprint.route('/suppliers-admin')
def suppliers_admin():
    suppliers = g.Supplier.get_all()
    return render_template('admin_panel/suppliers_admin.html', suppliers=suppliers)


@admin_blueprint.route('/suppliers-admin/<string:param>', methods=['GET', 'POST'])
def supplier_add_edit(param=None):
    if param == 'new':
        form = forms.SupplierForm()
    else:  # Edit user
        try:
            supplier = g.Supplier.find_by_id(param)
            form = forms.SupplierForm(**supplier.json(), supplier=supplier) # Create a form passing value of users for duplicate validations
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.suppliers_admin')

    if form.validate_on_submit():
        filled_form = {}
        for f in form:
            filled_form[f.name] = f.data
        del filled_form['csrf_token']
        if param == 'new':
            try:
                g.Supplier.add(**filled_form)
                flash(f"Proveedor: {filled_form['name']} fue agregado", ['success', 'popup'])
                return redirect(url_for('admin.suppliers_admin'))
            except Exception as e:
                    return render_template('admin_panel/error_pages/500.html', error=e, back_page='admin.suppliers_admin')
        else:
            try:
                supplier.update(**filled_form)
                flash(f"Proveedor: {filled_form['name']} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.suppliers_admin'))
            except Exception as e:
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/supplier_add_edit.html', form=form, supplier_model=g.Supplier,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/suppliers-admin/delete/<id>', methods=['GET', 'POST'])
@mustbe_admin
def supplier_delete(id):
    try:
        print(id)
        supplier = g.Supplier.find_by_id(id)
        name = supplier.name
        supplier.delete()
        flash(f'Proveedor: {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.suppliers_admin'))


'''
CUSTOMERS
'''


@admin_blueprint.route('/customers-admin')
def customers_admin():
    customers = g.Customer.get_all()
    return render_template('admin_panel/customers_admin.html', customers=customers)


@admin_blueprint.route('/customers-admin/<string:param>', methods=['GET', 'POST'])
def customer_add_edit(param=None):
    if param == 'new':
        form = forms.CustomerForm()
    else:  # Edit user
        try:
            customer = g.Customer.find_by_id(param)
            form = forms.CustomerForm(**customer.json(), customer=customer) # Create a form passing value of users for duplicate validations
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.customers_admin')

    if form.validate_on_submit():
        filled_form = {}
        for f in form:
            filled_form[f.name] = f.data
        del filled_form['csrf_token']
        if param == 'new':
            try:
                g.Customer.add(**filled_form)
                flash(f"Cliente: {filled_form['name']} fue agregado", ['success', 'popup'])
                return redirect(url_for('admin.customers_admin'))
            except Exception as e:
                    return render_template('admin_panel/error_pages/500.html', error=e, back_page='admin.customers_admin')
        else:
            try:
                customer.update(**filled_form)
                flash(f"Cliente: {filled_form['name']} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.customers_admin'))
            except Exception as e:
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/customer_add_edit.html', form=form, customer_model=g.Customer,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/customers-admin/delete/<id>', methods=['GET', 'POST'])
@mustbe_admin
def customer_delete(id):
    try:
        print(id)
        customer = g.Customer.find_by_id(id)
        name = customer.name
        customer.delete()
        flash(f'Cliente: {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.customers_admin'))


'''
MATERIALS
'''


@admin_blueprint.route('/materials-admin')
def materials_admin():
    materials = g.Material.get_all()
    return render_template('admin_panel/materials_admin.html', materials=materials)


@admin_blueprint.route('/materials-admin/<string:param>', methods=['GET', 'POST'])
def material_add_edit(param=None):
    if param == 'new':
        form = forms.MaterialForm()
    else:  # Edit user
        try:
            material = g.Material.find_by_id(param)
            form = forms.MaterialForm(**material.json(), material=material) # Create a form passing value of users for duplicate validations
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.materials_admin')

    if form.validate_on_submit():
        filled_form = {}
        for f in form:
            filled_form[f.name] = f.data
        del filled_form['csrf_token']
        if param == 'new':
            try:
                g.Material.add(**filled_form)
                flash(f"Material: {filled_form['name']} fue agregado", ['success', 'popup'])
                return redirect(url_for('admin.materials_admin'))
            except Exception as e:
                    return render_template('admin_panel/error_pages/500.html', error=e,
                                           back_page='admin.materials_admin')
        else:
            try:
                material.update(**filled_form)
                flash(f"Material: {filled_form['name']} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.materials_admin'))
            except Exception as e:
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/material_add_edit.html', form=form, material_model=g.Material,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/materials-admin/delete/<id>', methods=['GET', 'POST'])
@mustbe_admin
def material_delete(id):
    try:
        material = g.Material.find_by_id(id)
        name = material.name
        material.delete()
        flash(f'Material: {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.materials_admin'))


'''
MATERIAL BANKS
'''


@admin_blueprint.route('/banks-admin')
def banks_admin():
    banks = g.MaterialBank.get_all()
    return render_template('admin_panel/banks_admin.html', banks=banks)


@admin_blueprint.route('/banks-admin/<string:param>', methods=['GET', 'POST'])
def bank_add_edit(param=None):
    if param == 'new':
        form = forms.BankForm()
        form.owner_name.choices = [('', 'Seleccionar...')] + [(i, i) for i in g.Supplier.get_list_by('name')]
        form.material_name_list.choices = [(i, i) for i in g.Material.get_list_by('name')]
    else:  # Edit user
        try:
            bank = g.MaterialBank.find_by_id(param)
            form = forms.BankForm(**bank.json(), bank=bank)  # Create a form passing value of users for duplicate validations
            form.owner_name.choices = [('', 'Seleccionar...')] + [(i, i) for i in g.Supplier.get_list_by('name')]
            form.material_name_list.choices = [(i, i) for i in g.Material.get_list_by('name')]
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.banks_admin')

    if form.validate_on_submit():
        filled_form = {}
        for f in form:
            filled_form[f.name] = f.data
        del filled_form['csrf_token']
        if param == 'new':
            try:
                g.MaterialBank.add(**filled_form)
                flash(f"Banco: {filled_form['name']} fue agregado", ['success', 'popup'])
                return redirect(url_for('admin.banks_admin'))
            except Exception as e:
                    return render_template('admin_panel/error_pages/500.html', error=e,
                                           back_page='admin.banks_admin')
        else:
            try:
                bank.update(**filled_form)
                flash(f"Banco: {filled_form['name']} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.banks_admin'))
            except Exception as e:
                raise e
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/bank_add_edit.html', form=form, bank_model=g.MaterialBank,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/banks-admin/delete/<id>', methods=['GET', 'POST'])
@mustbe_admin
def bank_delete(id):
    try:
        bank = g.MaterialBank.find_by_id(id)
        name = bank.name
        bank.delete()
        flash(f'Banco: {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.banks_admin'))


'''
PROJECTS
'''


@admin_blueprint.route('/projects-admin')
def projects_admin():
    projects = g.Project.get_all()
    return render_template('admin_panel/projects_admin.html', projects=projects)


@admin_blueprint.route('/projects-admin/<string:param>', methods=['GET', 'POST'])
def project_add_edit(param=None):
    if param == 'new':
        form = forms.ProjectForm()
        form.customer_name.choices = [('', 'Seleccionar...')] + [(i, i) for i in g.Customer.get_list_by('name')]
        form.material_name_list.choices = [(i, i) for i in g.Material.get_list_by('name')]
    else:  # Edit user
        try:
            project = g.Project.find_by_id(param)
            form = forms.ProjectForm(**project.json(), project=project)  # Create a form passing value of object for duplicate validations
            form.customer_name.choices = [('', 'Seleccionar...')] + [(i, i) for i in g.Customer.get_list_by('name')]
            form.material_name_list.choices = [(i, i) for i in g.Material.get_list_by('name')]
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.projects_admin')

    if form.validate_on_submit():
        filled_form = {}
        for f in form:
            filled_form[f.name] = f.data
        del filled_form['csrf_token']
        if param == 'new':
            try:
                g.Project.add(**filled_form)
                flash(f"Obra: {filled_form['name']} fue agregado", ['success', 'popup'])
                return redirect(url_for('admin.projects_admin'))
            except Exception as e:
                    return render_template('admin_panel/error_pages/500.html', error=e,
                                           back_page='admin.projects_admin')
        else:
            try:
                project.update(**filled_form)
                flash(f"Obra: {filled_form['name']} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.projects_admin'))
            except Exception as e:
                print(e)
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/project_add_edit.html', form=form, project_model=g.Project,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/projects-admin/delete/<id>', methods=['GET', 'POST'])
@mustbe_admin
def project_delete(id):
    try:
        project = g.Project.find_by_id(id)
        name = project.name
        project.delete()
        flash(f'Obra: {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.projects_admin'))


'''
DRIVERS
'''


@admin_blueprint.route('/drivers-admin')
def drivers_admin():
    drivers = g.Driver.get_all()
    return render_template('admin_panel/drivers_admin.html', drivers=drivers)


@admin_blueprint.route('/drivers-admin/<string:param>', methods=['GET', 'POST'])
def driver_add_edit(param=None):
    if param == 'new':
        form = forms.DriverForm()
    else:  # Edit user
        try:
            driver = g.Driver.find_by_id(param)
            form = forms.DriverForm(**driver.json(), driver=driver)  # Create a form passing value of object for duplicate validations
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.drivers_admin')

    if form.validate_on_submit():
        filled_form = {}
        for f in form:
            filled_form[f.name] = f.data
        del filled_form['csrf_token']
        if param == 'new':
            try:
                g.Driver.add(**filled_form)
                flash(f"Chofer: {filled_form['name']} {filled_form['last_name']} fue agregado", ['success', 'popup'])
                return redirect(url_for('admin.drivers_admin'))
            except Exception as e:
                print(e)
                return render_template('admin_panel/error_pages/500.html', error=e,
                                           back_page='admin.drivers_admin')
        else:
            try:
                driver.update(**filled_form)
                flash(f"Chofer: {filled_form['name']} {filled_form['last_name']} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.drivers_admin'))
            except Exception as e:
                print(e)
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/driver_add_edit.html', form=form, driver_model=g.Driver,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/drivers-admin/delete/<id>', methods=['GET', 'POST'])
@mustbe_admin
def driver_delete(id):
    try:
        driver = g.Driver.find_by_id(id)
        name = driver.name
        driver.delete()
        flash(f'Chofer: {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.drivers_admin'))


'''
TRUCK
'''


@admin_blueprint.route('/trucks-admin')
def trucks_admin():
    trucks = g.Truck.get_all()
    return render_template('admin_panel/trucks_admin.html', trucks=trucks)


@admin_blueprint.route('/trucks-admin/<string:param>', methods=['GET', 'POST'])
def truck_add_edit(param=None):
    if param == 'new':
        form = forms.TruckForm()
        form.owner_name.choices = [('', 'Seleccionar...')] + [(i, i) for i in g.Supplier.get_list_by('name')]
        form.driver_full_name.choices = [('', 'Seleccionar...')] + [(i['id'], i['name'] + ' ' + i['last_name'])
                                                                    for i in g.Driver.get_all()]
    else:  # Edit user
        try:
            truck = g.Truck.find_by_id(param)
            form = forms.TruckForm(**truck.json(driver_id=True), truck=truck)  # Create a form passing value of object for duplicate validations
            form.owner_name.choices = [('', 'Seleccionar...')] + [(i, i) for i in g.Supplier.get_list_by('name')]
            form.driver_full_name.choices = [('', 'Seleccionar...')] + [(i['id'], i['name'] + ' ' + i['last_name'])
                                                                        for i in g.Driver.get_all()]
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.trucks_admin')

    if form.validate_on_submit():
        filled_form = {}
        for f in form:
            filled_form[f.name] = f.data
        del filled_form['csrf_token']
        if filled_form['driver_full_name']:
            driver = g.Driver.find_by_id(filled_form['driver_full_name'])
            filled_form['driver_full_name'] = (driver.name, driver.last_name)
        # print(filled_form)

        print("Encoding on stdout:")
        print(sys.stdout.encoding)
        print("Print string:")
        print("García Niño")
        print('García Niño')
        d = {'id_code': 'T4', 'brand': '', 'color': '', 'serial_number': '123', 'plate': '', 'capacity': 1,
             'driver_full_name': ('García García', 'García Niño'), 'owner_name': '', 'is_active': True}
        print("Printing dict:")
        print(d)

        if param == 'new':
            try:
                g.Truck.add(**filled_form)
                flash(f"Camión: {filled_form['id_code'].upper()} fue agregado", ['success', 'popup'])
                return redirect(url_for('admin.trucks_admin'))
            except Exception as e:
                print(e)
                return render_template('admin_panel/error_pages/500.html', error=e,
                                           back_page='admin.trucks_admin')
        else:
            try:
                truck.update(**filled_form)
                flash(f"Camión: {filled_form['id_code'].upper()} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.trucks_admin'))
            except Exception as e:
                print(e)
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/truck_add_edit.html', form=form, truck_model=g.Truck,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/trucks-admin/delete/<id>', methods=['GET', 'POST'])
@mustbe_admin
def truck_delete(id):
    try:
        truck = g.Truck.find_by_id(id)
        id_code = truck.id_code
        truck.delete()
        flash(f'Camión: {id_code} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.trucks_admin'))
