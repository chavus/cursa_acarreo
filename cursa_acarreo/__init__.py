from flask import Flask, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

login_manager = LoginManager()
app = Flask(__name__)


# Database setup
app.config['MONGODB_SETTINGS'] = {'host': 'mongodb+srv://dbuser:sa170687@cluster0-atrnj.mongodb.net/general?retryWrites=true&w=majority'}
app.config['SECRET_KEY'] = 'secretkey'


db = MongoEngine()
db.init_app(app)


login_manager.init_app(app)
login_manager.login_view = 'users.login'


@app.route('/')
def index():
    return redirect(url_for('trips.create'))


from cursa_acarreo.users.views import users_blueprint
from cursa_acarreo.trips.views import trips_blueprint


app.register_blueprint(users_blueprint)
app.register_blueprint(trips_blueprint)

