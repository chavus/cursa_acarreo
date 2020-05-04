from cursa_acarreo import app
from flask import redirect, url_for


@app.route('/')
def index():
    return redirect(url_for('trips.create'))


if __name__ == '__main__':
    app.run(debug=True)
