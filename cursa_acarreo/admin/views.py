from flask import Blueprint, render_template, flash, request, url_for, redirect
from cursa_acarreo.admin import forms
from cursa_acarreo.models.user import User
from cursa_acarreo.models import general as g
from flask_login import login_user, current_user, login_required, logout_user

admin_blueprint = Blueprint('admin', __name__)


@admin_blueprint.route('/base')
def admin_panel():
    return render_template('admin_panel/admin_base.html')


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
                flash(f"Usuario {user_new['username'].lower()} fue agregado", ['success', 'popup'])
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
                flash(f"Usuario {username.lower()} fue actualizado.", ['success', 'popup'])
                return redirect(url_for('admin.admin_users'))
            except Exception as e:
                flash(f"Error: {e}", ['error', 'popup'])
    return render_template('admin_panel/user_add_edit.html', form=form, user=User)


@admin_blueprint.route('/admin-users/delete/<username>', methods=['GET', 'POST'])
def user_delete(username):
    try:
        user = User.find_by_username(username)
        user.delete()
        flash(f'Usuario {username} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.admin_users'))


@admin_blueprint.route('/suppliers-admin')
def suppliers_admin():
    suppliers = g.Supplier.get_all()
    return render_template('admin_panel/suppliers_admin.html', suppliers=suppliers)


@admin_blueprint.route('/suppliers-admin/new', methods=['GET', 'POST'])
@admin_blueprint.route('/suppliers-admin/edit/<name>', methods=['GET', 'POST'])
def supplier_add_edit(name=None):
    pass


@admin_blueprint.route('/suppliers-admin/delete/<id>', methods=['GET', 'POST'])
def supplier_delete(id):
    try:
        print(id)
        supplier = g.Supplier.find_by_id(id)
        name = supplier.name
        supplier.delete()
        flash(f'Proveedor {name} fue eliminado.', ['success', 'popup'])
    except Exception as e:
        print(e)
        flash(f"Error: { e }", ['error', 'popup'])
    return redirect(url_for('admin.suppliers_admin'))