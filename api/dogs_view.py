from flask import Blueprint, make_response, jsonify, request
from bd import dogs


def create_dogs_blueprint():
    dogs_blueprint = Blueprint('dogs', __name__)

    @dogs_blueprint.route('/dogs', methods=['GET'])
    def get_dogs():
        return make_response(jsonify(message='Lista de cahorros', data=dogs))

    @dogs_blueprint.route('/dogs', methods=['POST'])
    def create_dogs():
        return make_response(jsonify(message='Cachorro cadastrado com sucesso', data=request.json))

    return dogs_blueprint
