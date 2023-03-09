from flask import Flask, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
import locale
import pytz
import os
import git
from dotenv import load_dotenv

login_manager = LoginManager()
app = Flask(__name__)

project_dir = os.getcwd()

locale.setlocale(locale.LC_ALL, 'es_ES')

# Database setup (to move to settings.py later)
load_dotenv()  # Load environment vars to run locally
environment = os.environ.get('ENVIRONMENT')
if not environment:
    print('No heroku environment found, trying if git repository.')
    try:
        current_dir = os.getcwd()
        branch = git.Repo(current_dir).active_branch.name
        environment = branch
    except git.exc.InvalidGitRepositoryError as e:
        print('Directory not a git repositoy... running with development configuration.')


if environment in ['master', 'production']:
    db_pwd = os.environ.get('PROD_DB_PWD')
    db_user = os.environ.get('PROD_DB_USER')
    app.config['MONGODB_SETTINGS'] = {'host': f'mongodb+srv://{db_user}:{db_pwd}@cluster0-atrnj.mongodb.net/general?retryWrites=true&w=majority',
                                      'connect': False}
    print('Configuring as master/production environment')
    app_env = 'PROD'
else:
    db_pwd = os.environ.get('DEV_DB_PWD')
    db_user = os.environ.get('DEV_DB_USER')
    app.config['MONGODB_SETTINGS'] = {'host': f'mongodb+srv://{db_user}:{db_pwd}@cursaacarreocluster-dev-gjrrh.mongodb.net/general?retryWrites=true&w=majority',
                                      'connect': False}
    print('Configuring as development environment')
    app_env = 'DEV'


app.config['SECRET_KEY'] = 'secretkey'  # >`o"Lb0bR@yMc<|&GM6g,nCQd([?-6|8QHNLAKc,l~^4]Lq,g(&h9tn$,uxQTn@
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['ENV'] = app_env


@app.template_filter()
def formatdate_mx(datetime_val):
    if datetime_val:
        timezone = pytz.timezone('America/Mexico_City')
        mx_time = timezone.fromutc(datetime_val)
        return mx_time.strftime("%d-%b-%Y %H:%M")
    else:
        return ""

db = MongoEngine()
db.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'users.login'
login_manager.login_message = 'Ingresa tus credenciales para acceder!'


@app.route('/')
def index():
    return redirect(url_for('users.login'))


from cursa_acarreo.users.views import users_blueprint
from cursa_acarreo.trips.views import trips_blueprint
from cursa_acarreo.admin.views import admin_blueprint
from cursa_acarreo.error_pages.handlers import error_pages

app.register_blueprint(users_blueprint)
app.register_blueprint(trips_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(error_pages)
