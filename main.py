from flask import Flask
from flask_wtf.csrf import CSRFProtect
from forms import *
import dict
from api.dogs_view import create_dogs_blueprint
from models import db
from routes import blueprint
import pandas as pd

app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400
app.register_blueprint(create_dogs_blueprint())
app.register_blueprint(blueprint)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///adoption.sqlite3'





if __name__ == "__main__":

    key = 'SADS214@@'
    db.init_app(app)

    with app.app_context():
        db.create_all()
        df = pd.read_sql_query("SELECT * FROM dogs", db.engine)
    app.config['SECRET_KEY'] = key
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.run(debug=True)
    app.secret_key = key
    csrf = CSRFProtect(app)
    csrf.init_app(app)
