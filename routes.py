from flask import Blueprint,render_template, request, redirect, url_for, jsonify, session
from models import *
from forms import *

blueprint = Blueprint("bp", __name__)



@blueprint.route('/')
def index():
    name = session.get("name")
    return render_template("index.html", name=name)


@blueprint.route('/users', methods=["GET"])
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    all_users = User.query.paginate(page=page, per_page=per_page)
    return render_template("users.html", users=all_users)


@blueprint.route("/user/register", methods=["POST", "GET"])
def user_register():
    form = UserRegisterForm(request.form)
    if request.method == "POST" and form.validate():
        existing_user = User.query.filter_by(email=form.regEmail.data).first()
        if existing_user:
            return "A user with this email address already exists. Please use a different email address."
        user = User(cpf=form.regCPF.data, name=form.regName.data, email=form.regEmail.data, phone=form.regPhone.data,
                    password=form.regPassword.data, user_level=0, date_register=form.regDateRegister.data,
                    city=form.regCity.data, state=form.regState.data, address=form.regAddress.data,
                    zipCode=form.regZipCode.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users'))
    return render_template("register.html", form=form)


@blueprint.route('/<string:cpf>/update_user', methods=["GET", "POST"])
def update_user(cpf):
    user = User.query.filter_by(cpf=cpf).first()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        date_register_str = request.form["date_register"]
        date_register = datetime.strptime(date_register_str, "%Y-%m-%d %H:%M:%S")
        state = request.form["state"]
        city = request.form["city"]
        address = request.form["address"]
        zipCode = request.form["zipCode"]
        User.query.filter_by(cpf=cpf).update({"name": name, "email": email, "phone": phone, "password": password,
                                              "date_register": date_register, "state": state, "city": city,
                                              "address": address, "zipCode": zipCode})
        db.session.commit()
        return redirect(url_for('users'))
    return render_template("update_user.html", user=user)


@blueprint.route('/<string:cpf>/remove_user', methods=["GET", "POST"])
def remove_user(cpf):
    user = User.query.filter_by(cpf=cpf).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("users"))


@blueprint.route("/user/login", methods=["POST", "GET"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        name = form.loginName.data
        password = form.loginPwd.data

        users = User.query.all()

        for user in users:

            if user.password == password:

                session["name"] = user.cpf
                session.permanent = True
                return redirect('/')
        redirect(url_for('login'))

    return render_template("login.html", form=form)


@blueprint.route('/dogs', methods=["GET"])
def dogs():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    all_dogs = Dogs.query.paginate(page=page, per_page=per_page)
    return render_template("dogs.html", dogs=all_dogs)


@blueprint.route('/add_dog', methods=["GET", "POST"])
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


@blueprint.route('/<int:id>/update_dog', methods=["GET", "POST"])
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


@blueprint.route('/<int:id>/remove_dog', methods=["GET", "POST"])
def remove_dog(id):
    dog = Dogs.query.filter_by(id=id).first()
    db.session.delete(dog)
    db.session.commit()
    return redirect(url_for("dogs"))



@blueprint.route('/preferences', methods=["GET", "POST"])
def preferences():
    global df

    cluster_df = df.drop(columns=['name', 'photo'])

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

        matching_rows = pd.merge(matching_rows, df[['id', 'name', 'photo']], on='id')

        matching_rows = matching_rows.drop(matching_rows.index[-1])

        matching_rows = dict.convert_integer_to_string(matching_rows.to_dict(orient='records'))

        return render_template('suggestions.html', rows=matching_rows)

    return render_template("preferences.html")