from flask import Flask, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
import locale
import pytz

login_manager = LoginManager()
app = Flask(__name__)

locale.setlocale(locale.LC_ALL, 'es_ES')


# Database setup
app.config['MONGODB_SETTINGS'] = {'host': 'mongodb+srv://dbuser:sa170687@cluster0-atrnj.mongodb.net/general?retryWrites=true&w=majority'}
app.config['SECRET_KEY'] = 'secretkey'


@app.template_filter()
def formatdate_mx(datetime_val):
    timezone = pytz.timezone('America/Mexico_City')
    mx_time = timezone.fromutc(datetime_val)
    return mx_time.strftime("%d-%b-%Y %H:%M")


db = MongoEngine()
db.init_app(app)


login_manager.init_app(app)
login_manager.login_view = 'users.login'

@app.route('/')
def index():
    return redirect(url_for('trips.create'))


from cursa_acarreo.users.views import users_blueprint
from cursa_acarreo.trips.views import trips_blueprint
from cursa_acarreo.error_pages.handlers import error_pages

app.register_blueprint(users_blueprint)
app.register_blueprint(trips_blueprint)
app.register_blueprint(error_pages)
