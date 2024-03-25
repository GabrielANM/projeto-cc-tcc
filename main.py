from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from wtforms import StringField, SubmitField, PasswordField, validators
from flask_sqlalchemy import SQLAlchemy
from sklearn.preprocessing import StandardScaler
from flask_wtf.csrf import CSRFProtect

from datetime import datetime
from forms import *


import dict
from api.dogs_view import create_dogs_blueprint
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer

app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400
app.register_blueprint(create_dogs_blueprint())


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///adoption.sqlite3'
db = SQLAlchemy(app)


class Dogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.String(50))
    sex = db.Column(db.String(50))
    size = db.Column(db.String(50))
    fixed = db.Column(db.String(50))
    house_trained = db.Column(db.String(50))
    special_needs = db.Column(db.String(50))
    shots_current = db.Column(db.String(50))
    env_children = db.Column(db.String(50))
    env_dogs = db.Column(db.String(50))
    env_cats = db.Column(db.String(50))
    photo = db.Column(db.String(50))

    def __init__(self, name, age, sex, size, fixed, house_trained,
                 special_needs, shots_current, env_children, env_dogs, env_cats, photo):
        self.name = name
        self.age = age
        self.sex = sex
        self.size = size
        self.fixed = fixed
        self.house_trained = house_trained
        self.special_needs = special_needs
        self.shots_current = shots_current
        self.env_children = env_children
        self.env_dogs = env_dogs
        self.env_cats = env_cats
        self.photo = photo


class User(db.Model):



    cpf = db.Column(db.String(11), primary_key=True, nullable=False)
    name = db.Column(db.String(50), primary_key=True, nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    phone = db.Column(db.String(13))
    password = db.Column (db.String(50), nullable=False)
    user_level = db.Column (db.Integer, nullable=False)
    date_register = db.Column(db.DateTime, default=datetime.now())
    city = db.Column(db.String(29))
    state = db.Column(db.String(15))
    address = db.Column(db.String(50))
    zipCode = db.Column(db.String(10))

    def __repr__(self):
        return f'Name: {self.name}'

    def __init__(self, cpf, name, email, phone, password, user_level, date_register, city, state,
                 address, zipCode):
        self.cpf= cpf
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.user_level = user_level
        self.date_register = date_register
        self.city = city
        self.state = state
        self.address = address
        self.zipCode = zipCode



#routes



@app.route('/')
def index():
    name = session.get("name")
    return render_template("index.html", name=name)

@app.route("/user/register", methods=["POST", "GET"])
def user_register():

    form = UserRegisterForm()

    if form.validate_on_submit():

        cpf = form.regCPF.data
        name = form.regName.data
        email = form.regEmail.data
        phone = form.regPhone.data
        password = form.regPassword.data
        date = form.regDateRegister.data
        state = form.regState.data
        city = form.regState.data
        address = form.regAddress.data
        zipCode = form.regZipCode.data

        user = User(cpf=cpf, name=name, email=email, phone=phone, password=password, user_level = 0,
                    date_register=date, city=city, state=state, address=address, zipCode=zipCode)

        db.session.add(user)
        db.session.commit()
        return "User added successfully!!!"

    return render_template("register.html", form=form)

@app.route("/user/login", methods=["POST", "GET"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        name = form.loginName.data
        password = form.loginPwd.data

        users = User.query.all()

        for user in users:

            print(f"Typed: {password}\nPass {user.password}")

            if user.password == password:

                session["name"] = user.cpf
                session.permanent = True
                return redirect('/')
            else:

                redirect(url_for('login'))







        # Login with SQLAlchemy

    return render_template("login.html", form=form)


@app.route('/dogs', methods=["GET"])
def dogs():
    return render_template("dogs.html", dogs=Dogs.query.all())


@app.route('/add_dog', methods=["GET", "POST"])
def add_dog():
    name = request.form.get("name")
    age = request.form.get("age")
    sex = request.form.get("sex")
    size = request.form.get("size")
    fixed = request.form.get("fixed")
    house_trained = request.form.get("house_trained")
    special_needs = request.form.get("special_needs")
    shots_current = request.form.get("shots_current")
    env_children = request.form.get("env_children")
    env_dogs = request.form.get("env_dogs")
    env_cats = request.form.get("env_cats")
    photo = request.form.get("photo")

    if request.method == "POST":
        dog = Dogs(name, age, sex, size, fixed, house_trained,
                   special_needs, shots_current, env_children, env_dogs, env_cats, photo)
        db.session.add(dog)
        db.session.commit()
        return redirect(url_for('dogs'))
    return render_template("new_dog.html")


def cluster_data(df):
    imputer = SimpleImputer(strategy='mean')
    df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    num_clusters = 2
    kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=0).fit(df_imputed)
    df_clustered = pd.DataFrame(df_imputed, columns=df.columns)
    df_clustered['cluster'] = kmeans.labels_

    return df_clustered


@app.route('/preferences', methods=["GET", "POST"])
def preferences():
    global df

    cluster_df = df[['age',
                     'sex',
                     'size',
                     'fixed',
                     'house_trained',
                     'special_needs',
                     'shots_current',
                     'env_children',
                     'env_dogs',
                     'env_cats', ]].copy()

    if request.method == "POST":
        data = {
            "age": request.form.get("age"),
            "sex": request.form.get("sex"),
            "size": request.form.get("size"),
            "fixed": request.form.get("fixed"),
            "house_trained": request.form.get("house_trained"),
            "special_needs": request.form.get("special_needs"),
            "shots_current": request.form.get("shots_current"),
            "env_children": request.form.get("env_children"),
            "env_dogs": request.form.get("env_dogs"),
            "env_cats": request.form.get("env_cats"),
        }

        new_row = pd.DataFrame([data])

        data_frame = pd.concat([cluster_df, new_row], ignore_index=True)

        data_frame = dict.convert_string_to_integer(data_frame)

        clustered_df = cluster_data(data_frame)
        new_row_cluster = clustered_df.iloc[-1]['cluster']
        matching_rows = clustered_df[clustered_df['cluster'] == new_row_cluster].drop(columns=['cluster'])
        matching_rows = dict.convert_integer_to_string(matching_rows.to_dict(orient='records'))

        return render_template('suggestions.html', rows=matching_rows)

    return render_template("preferences.html")





if __name__ == "__main__":

    key = 'SADS214@@'

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




