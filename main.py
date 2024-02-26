from flask import Flask, render_template, request
from api.dogs_view import create_dogs_blueprint


app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False
app.register_blueprint(create_dogs_blueprint())


@app.route('/')
def index():
    return render_template("index.html")


dogs = []
dict_dogs = []


@app.route('/aboutus',  methods=["GET", "POST"])
def aboutus():
    if request.method == "POST":
        if request.form.get("dog") and request.form.get("tutor"):
            dict_dogs.append({"dog": request.form.get("dog"), "tutor": request.form.get("tutor")})
    return render_template("aboutus.html", dict_dogs=dict_dogs)


@app.route('/indexcurso',  methods=["GET", "POST"])
def indexcurso():
    if request.method == "POST":
        if request.form.get("dogs"):
            dogs.append(request.form.get("dogs"))
    return render_template("indexcurso.html", dogs=dogs)


app.run()
