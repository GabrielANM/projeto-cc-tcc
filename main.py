from flask import Flask, render_template
from api.dogs_view import create_dogs_blueprint


app = Flask("Adoption")
app.config['JSON_SORT_KEYS'] = False
app.register_blueprint(create_dogs_blueprint())


@app.route('/')
def index():
    return render_template("index.html")


app.run()
