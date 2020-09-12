from flask import Blueprint, render_template, flash, request, url_for, redirect
from cursa_acarreo.admin import forms
from cursa_acarreo.models.user import User
from cursa_acarreo.models import general as g
from flask_login import login_user, current_user, login_required, logout_user

admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('/base')
def admin_panel():
    return render_template('admin_panel/admin_base.html')

@admin_blueprint.route('/test')
def admin_test():
    return render_template('admin_panel/admin_test.html')

'''
USERS
'''


@admin_blueprint.route('/admin-users')
def admin_users():
    users = User.get_all()
    return render_template('admin_panel/admin_users.html', users=users)


@admin_blueprint.route('/admin-users/new', methods=['GET', 'POST'])
@admin_blueprint.route('/admin-users/edit/<username>', methods=['GET', 'POST'])
def user_add_edit(username=None):
    if username:
        try:
            user = User.find_by_username(username)
            form = forms.UserForm(**user.json(), user=user) # Create a form passing value of users for duplicate validations
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
                print((filled_form['name']))
                flash(f"Material: {filled_form['name']} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.materials_admin'))
            except Exception as e:
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/material_add_edit.html', form=form, material_model=g.Material,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/materials-admin/delete/<id>', methods=['GET', 'POST'])
def material_delete(id):
    try:
        print(id)
        material = g.Material.find_by_id(id)
        name = material.name
        material.delete()
        flash(f'Material: {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
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
            print(bank.json())
            form = forms.BankForm(**bank.json(), bank=bank)  # Create a form passing value of users for duplicate validations
            form.owner_name.choices = [('', 'Seleccionar...')] + [(i, i) for i in g.Supplier.get_list_by('name')]
            form.material_name_list.choices = [(i, i) for i in g.Material.get_list_by('name')]
        except Exception as e:
            return render_template('admin_panel/error_pages/404.html', error=e, back_page='admin.banks_admin')

    if request.method == 'POST':
        print(form.is_active.data)

    if form.validate_on_submit():
        filled_form = {}
        for f in form:
            filled_form[f.name] = f.data
        del filled_form['csrf_token']
        print(filled_form)
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
                print((filled_form['name']))
                flash(f"Banco: {filled_form['name']} fue actualizado", ['success', 'popup'])
                return redirect(url_for('admin.banks_admin'))
            except Exception as e:
                raise e
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/bank_add_edit.html', form=form, bank_model=g.MaterialBank,
                           action='create' if param == 'new' else 'edit')


@admin_blueprint.route('/banks-admin/delete/<id>', methods=['GET', 'POST'])
def bank_delete(id):
    try:
        print(id)
        bank = g.MaterialBank.find_by_id(id)
        name = bank.name
        bank.delete()
        flash(f'Banco: {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.banks_admin'))
