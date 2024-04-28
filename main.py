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
from functools import wraps

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
        self.cpf = cpf
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


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_level = session.get('user_level', 0)
        if user_level != 1:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    name = session.get("name")
    return render_template("index.html", name=name)


@app.route('/users', methods=["GET"])
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    all_users = User.query.paginate(page=page, per_page=per_page)
    return render_template("users.html", users=all_users)


@app.route("/user/register", methods=["POST", "GET"])
@admin_required
def user_register():
    form = UserRegisterForm(request.form)
    if request.method == "POST" and form.validate():
        existing_user = User.query.filter_by(email=form.regEmail.data).first()
        if existing_user:
            return "Um usuário com esse email ja existe. Por favor utilize um endereço de email diferente"
        user = User(cpf=form.regCPF.data, name=form.regName.data, email=form.regEmail.data, phone=form.regPhone.data,
                    password=form.regPassword.data, user_level=0, date_register=form.regDateRegister.data,
                    city=form.regCity.data, state=form.regState.data, address=form.regAddress.data,
                    zipCode=form.regZipCode.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users'))
    return render_template("register.html", form=form)


@app.route('/<string:cpf>/update_user', methods=["GET", "POST"])
@admin_required
def update_user(cpf):
    user = User.query.filter_by(cpf=cpf).first()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        user_level = int(request.form["user_level"])
        date_register_str = request.form["date_register"]
        date_register = datetime.strptime(date_register_str, "%Y-%m-%d %H:%M:%S")
        state = request.form["state"]
        city = request.form["city"]
        address = request.form["address"]
        zipCode = request.form["zipCode"]
        User.query.filter_by(cpf=cpf).update({"name": name, "email": email, "phone": phone, "password": password,
                                              "user_level": user_level,"date_register": date_register, "state": state,
                                              "city": city, "address": address, "zipCode": zipCode})
        db.session.commit()
        return redirect(url_for('users'))
    return render_template("update_user.html", user=user)


@app.route('/<string:cpf>/remove_user', methods=["GET", "POST"])
@admin_required
def remove_user(cpf):
    user = User.query.filter_by(cpf=cpf).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("users"))


# @app.route("/user/login", methods=["POST", "GET"])
# def login():
#
#     form = LoginForm()
#
#     if form.validate_on_submit():
#
#         name = form.loginName.data
#         password = form.loginPwd.data
#
#         users = User.query.all()
#
#         for user in users:
#
#             if user.password == password:
#
#                 session["name"] = user.cpf
#                 session.permanent = True
#                 return redirect('/')
#         redirect(url_for('login'))
#
#     return render_template("antigologin.html", form=form)


@app.route("/user/login", methods=["GET", "POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user and user.password == password:
        session["email"] = user.email
        session["user_level"] = user.user_level
        session.permanent = True
        return redirect(url_for('index'))
    else:
        return render_template("login.html", user=user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dogs', methods=["GET"])
@admin_required
def dogs():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    all_dogs = Dogs.query.paginate(page=page, per_page=per_page)
    return render_template("dogs.html", dogs=all_dogs)


@app.route('/add_dog', methods=["GET", "POST"])
@admin_required
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


@app.route('/<int:id>/update_dog', methods=["GET", "POST"])
@admin_required
def update_dog(id):
    dog = Dogs.query.filter_by(id=id).first()
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        sex = request.form["sex"]
        size = request.form["size"]
        fixed = request.form["fixed"]
        house_trained = request.form["house_trained"]
        special_needs = request.form["special_needs"]
        shots_current = request.form["shots_current"]
        env_children = request.form["env_children"]
        env_dogs = request.form["env_dogs"]
        env_cats = request.form["env_cats"]
        photo = request.form["photo"]
        Dogs.query.filter_by(id=id).update({"name": name, "age": age, "sex": sex, "size": size, "fixed": fixed,
                                            "house_trained": house_trained, "special_needs": special_needs,
                                            "shots_current": shots_current, "env_children": env_children,
                                            "env_dogs": env_dogs, "env_cats": env_cats, "photo": photo})
        db.session.commit()
        return redirect(url_for("dogs"))
    return render_template("update_dog.html", dog=dog)


@app.route('/<int:id>/remove_dog', methods=["GET", "POST"])
@admin_required
def remove_dog(id):
    dog = Dogs.query.filter_by(id=id).first()
    db.session.delete(dog)
    db.session.commit()
    return redirect(url_for("dogs"))


def cluster_data(df):
    imputer = SimpleImputer(strategy='mean')
    df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    df_clustered = pd.DataFrame(df_imputed, columns=df.columns)
    df_clustered['cluster'] = KMeans(n_clusters=num_clusters).fit_predict(df_imputed)

    return df_clustered


@app.route('/preferences', methods=["GET", "POST"])
def preferences():
    global df

    if request.method == "POST":
        data = {
            "id": df['id'].max() + 1,  # Add this line
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

        new_row = dict.convert_string_to_integer(new_row)

        data_frame = pd.concat([df, new_row], ignore_index=True)

        # Retrain the KMeans model with the new data
        kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=0)
        kmeans.fit(data_frame)

        clustered_df = cluster_data(data_frame)
        new_row_cluster = clustered_df.iloc[-1]['cluster']
        matching_rows = clustered_df[clustered_df['cluster'] == new_row_cluster].drop(columns=['cluster'])

        matching_rows = pd.merge(matching_rows, original_df[['id', 'name', 'photo']], on='id')

        matching_rows = matching_rows.drop(matching_rows.index[-1])

        matching_rows = dict.convert_integer_to_string(matching_rows.to_dict(orient='records'))

        return render_template('suggestions.html', rows=matching_rows)

    return render_template("preferences.html")


key = 'SADS214@@'
with app.app_context():
    db.create_all()
    df = pd.read_sql_query("SELECT * FROM dogs", db.engine)
    df = dict.convert_string_to_integer(df)

    num_clusters = 6
    kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=0)

    original_df = df.copy()
    df = df.drop(columns=['name', 'photo'])

    kmeans.fit(df)

app.config['SECRET_KEY'] = key
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.run()
app.secret_key = key
