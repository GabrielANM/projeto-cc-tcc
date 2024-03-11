from flask import Blueprint, make_response, jsonify, request


def create_dogs_blueprint():
    dogs_blueprint = Blueprint('dogs', __name__)

    return dogs_blueprint
