from flask import Blueprint, render_template, flash, request, url_for, redirect
from cursa_acarreo.users.forms import LoginForm
from cursa_acarreo.models.user import User

from flask_login import login_user, current_user, login_required, logout_user

users_blueprint = Blueprint('users', __name__)


# @users_blueprint.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.find_by_username(form.username.data)
#         if user.check_password(form.password.data):
#             login_user(user)
#             # flash('Bienvenido {}!'.format(current_user.name.title()), ('primary',))
#             next = request.args.get('next')
#
#             if not next:
#                 next = url_for('trips.create_home')
#             return redirect(next)
#         else:
#             form.password.errors.append('Contraseña incorrecta')
#     return render_template('login.html', form=form)

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_username(form.username.data)
        if user.check_password(form.password.data):
            login_user(user)
            # flash('Bienvenido {}!'.format(current_user.name.title()), ('primary',))
            next = request.args.get('next')
            if not next:
                next = url_for('admin.general_admin') if current_user.role == 'admin' else url_for('trips.create_home')
                # next = url_for('trips.create_home')

            return redirect(next)
        else:
            form.password.errors.append('Contraseña incorrecta')
    return render_template('login.html', form=form)


@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('Hasta pronto!')
    return redirect(url_for('users.login'))
