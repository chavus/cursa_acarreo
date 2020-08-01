from flask import Flask, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
import locale
import pytz
import os
import git
import json

login_manager = LoginManager()
app = Flask(__name__)

project_dir = os.getcwd()

locale.setlocale(locale.LC_ALL, 'es_ES')

# Database setup
environment = os.environ.get('ENVIRONMENT')
if not environment:
    print('No heroku environment found, trying if git repository.')
    try:
        current_dir = os.getcwd()
        branch = git.Repo(current_dir).active_branch.name
        environment = branch
    except git.exc.InvalidGitRepositoryError as e:
        print('Directory not a git repositoy... running with development configuration.')


if environment == 'master' or environment == 'production':
    app.config['MONGODB_SETTINGS'] = {'host': 'mongodb+srv://dbuser:sa170687@cluster0-atrnj.mongodb.net/general?retryWrites=true&w=majority',
                                      'connect': False}
    print('Configuring as master/production environment')
    app_env = 'PROD'
else:
    app.config['MONGODB_SETTINGS'] = {'host': 'mongodb+srv://dbuser:sa170687@cursaacarreocluster-dev-gjrrh.mongodb.net/general?retryWrites=true&w=majority',
                                      'connect': False}
    print('Configuring as development environment')
    app_env = 'DEV'


app.config['SECRET_KEY'] = 'secretkey'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.template_filter()
def formatdate_mx(datetime_val):
    timezone = pytz.timezone('America/Mexico_City')
    mx_time = timezone.fromutc(datetime_val)
    return mx_time.strftime("%d-%b-%Y %H:%M")


db = MongoEngine()
db.init_app(app)


login_manager.init_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message = 'Ingresa tus credenciales para acceder!'

@app.route('/')
def index():
    return redirect(url_for('trips.create_home'))


@app.route('/test')
def test():
    return json.dumps({'GRAVA 1.5"': 'GRAVA 1.5"', 'val2': 'val2'})


from cursa_acarreo.users.views import users_blueprint
from cursa_acarreo.trips.views import trips_blueprint
from cursa_acarreo.error_pages.handlers import error_pages

app.register_blueprint(users_blueprint)
app.register_blueprint(trips_blueprint)
app.register_blueprint(error_pages)
