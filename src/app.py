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
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
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

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route("/signup", methods=["POST"])
def signup():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    existing_user = db.session.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if existing_user:
        return jsonify({"msg": "Email already registered"}), 409

    new_user = User(email=email, password=password, is_active=True)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201


@app.route("/login", methods=["POST"])
def login():

    email = request.json.get("email", None)
    password = request.json.get("password", None)

    query_user = db.session.execute(select(User).where(
        User.email == email)).scalar_one_or_none()
    if query_user is None:
        return jsonify({"msg": "User not exist"}), 404
    if email != query_user.email or password != query_user.password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=str(query_user.id))
    return jsonify(access_token=access_token)


@app.route("/private", methods=["GET"])
@jwt_required()
def protected():

    current_user = get_jwt_identity()

    query_user = db.session.execute(select(User).where(
        User.id == int(current_user))).scalar_one_or_none()

    user_favorites = db.session.execute(select(Favorite).where(
        Favorite.user_id == query_user.id)).scalars().all()
    results = list(map(lambda item: item.serialize(), user_favorites))

    return jsonify({"results": results}), 200


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


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
@jwt_required()
def add_favorite_planet(planet_id):
    user_id = get_jwt_identity()

    planet = db.session.get(Planet, planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    existing = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.planet_id == planet_id
        )
    ).scalar_one_or_none()

    if existing:
        return jsonify({"message": "This planet is already on favorites"}), 409

    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Planet added to favorites", "favorite": new_favorite.serialize()}), 201


@app.route('/favorite/character/<int:character_id>', methods=['POST'])
@jwt_required()
def add_favorite_character(character_id):
    user_id = get_jwt_identity()

    character = db.session.get(Character, character_id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404

    existing = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.character_id == character_id
        )
    ).scalar_one_or_none()

    if existing:
        return jsonify({"message": "This character is already on favorites"}), 409

    new_favorite = Favorite(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"message": "Character added to favorites", "favorite": new_favorite.serialize()}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_planet(planet_id):
    user_id = get_jwt_identity()

    favorite = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.planet_id == planet_id
        )
    ).scalar_one_or_none()

    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Planet deleted from favorites"}), 200


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_character(character_id):
    user_id = get_jwt_identity()

    favorite = db.session.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.character_id == character_id
        )
    ).scalar_one_or_none()

    if favorite is None:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "PCharacter deleted from favorites"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
