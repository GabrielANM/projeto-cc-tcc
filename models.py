from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer


db = SQLAlchemy()


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




def cluster_data(df):
    imputer = SimpleImputer(strategy='mean')
    df_imputed = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    num_clusters = 2
    kmeans = KMeans(n_clusters=num_clusters, init='k-means++', random_state=0).fit(df_imputed)
    df_clustered = pd.DataFrame(df_imputed, columns=df.columns)
    df_clustered['cluster'] = kmeans.labels_

    return df_clustered