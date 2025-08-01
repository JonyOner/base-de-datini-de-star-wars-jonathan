"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Vehicle, Character, Favorite
from sqlalchemy import select
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users', methods=['GET'])
def get_all_users():

    all_users = db.session.execute(select(User)).scalars().all()
    results = list(map(lambda item: item.serialize(), all_users))

    response_body = {
        "results": results
    }

    return jsonify(response_body), 200


@app.route('/users/<int:id>', methods=['GET'])
def get_one_user(id):

    one_user = db.session.get(User, id)

    response_body = {
        "results": one_user.serialize()
    }

    return jsonify(response_body), 200


@app.route('/planets', methods=['GET'])
def get_all_planets():

    all_planets = db.session.execute(select(Planet)).scalars().all()
    results = list(map(lambda item: item.serialize(), all_planets))

    response_body = {
        "results": results
    }

    return jsonify(response_body), 200


@app.route('/planets/<int:id>', methods=['GET'])
def get_one_planet(id):

    one_planet = db.session.get(Planet, id)

    response_body = {
        "results": one_planet.serialize()
    }

    return jsonify(response_body), 200


@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():

    all_vehicles = db.session.execute(select(Vehicle)).scalars().all()
    results = list(map(lambda item: item.serialize(), all_vehicles))

    response_body = {
        "results": results
    }

    return jsonify(response_body), 200


@app.route('/vehicles/<int:id>', methods=['GET'])
def get_one_vehicle(id):

    one_vehicle = db.session.get(Vehicle, id)

    response_body = {
        "results": one_vehicle.serialize()
    }

    return jsonify(response_body), 200


@app.route('/characters', methods=['GET'])
def get_all_characters():

    all_characters = db.session.execute(select(Character)).scalars().all()
    results = list(map(lambda item: item.serialize(), all_characters))

    response_body = {
        "results": results
    }

    return jsonify(response_body), 200


@app.route('/characters/<int:id>', methods=['GET'])
def get_one_character(id):

    one_character = db.session.get(Character, id)

    response_body = {
        "results": one_character.serialize()
    }

    return jsonify(response_body), 200


@app.route('/favorites', methods=['GET'])
def get_all_favorites():

    all_favorites = db.session.execute(select(Favorite)).scalars().all()
    results = list(map(lambda item: item.serialize(), all_favorites))

    response_body = {
        "results": results
    }

    return jsonify(response_body), 200


@app.route('/favorites/<int:id>', methods=['GET'])
def get_one_favorite(id):

    one_favorite = db.session.get(Favorite, id)

    response_body = {
        "results": one_favorite.serialize()
    }

    return jsonify(response_body), 200


@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_all_user_favorites(user_id):

    query_user = db.session.execute(select(User).where(
        User.id == user_id)).scalar_one_or_none()

    response_body = {
        "results": query_user.all_user_favorites()
    }

    return jsonify(response_body), 200



#@app.route('/user', methods=['POST'])
#def add_new_user():
    #request_body = request.json
    #new_user = User(request_body)

    #db.session.add(new_user)
    #db.session.commit()

    #return jsonify({"msg": "user created"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
