#!/usr/bin/env python3
from models import db, Hero, Power
from flask import Flask, make_response, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from models import db, Hero
from flask import jsonify
from flask import request
from models import db, Hero, Power, HeroPower





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///heroes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return 'SUPER HEROES'

@app.route('/', methods=['GET'])
def welcome():
    welcome_message = "Welcome to my Super Hero List."
    return render_template('welcome.html', message=welcome_message)

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    hero_data = [{"id": hero.id, "name": hero.name, "super_name": hero.super_name} for hero in heroes]
    return jsonify(hero_data)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if hero is None:
        return jsonify({"error": "Hero not found"}), 404
    powers = [{"id": power.id, "name": power.name, "description": power.description} for power in hero.powers]
    hero_data = {"id": hero.id, "name": hero.name, "super_name": hero.super_name, "powers": powers}
    return jsonify(hero_data)

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    power_data = [{"id": power.id, "name": power.name, "description": power.description} for power in powers]
    return jsonify(power_data)

@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({"error": "Power not found"}), 404
    power_data = {"id": power.id, "name": power.name, "description": power.description}
    return jsonify(power_data)

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.json
    strength = data.get("strength")
    power_id = data.get("power_id")
    hero_id = data.get("hero_id")

    # Validate the strength (use the HeroPower validation)
    try:
        validated_strength = HeroPower().validate_strength("strength", strength)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Validate that the power and hero exist
    power = Power.query.get(power_id)
    hero = Hero.query.get(hero_id)

    if not power:
        return jsonify({"error": "Power not found"}), 404

    if not hero:
        return jsonify({"error": "Hero not found"}), 404

    # Create a new HeroPower association and add it to the database
    hero_power = HeroPower(strength=validated_strength, hero_id=hero_id, power_id=power_id)
    db.session.add(hero_power)
    db.session.commit()

    # Return the data related to the hero as described in the prompt
    powers = [{"id": p.id, "name": p.name, "description": p.description} for p in hero.powers]
    hero_data = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "powers": powers
    }
    return jsonify(hero_data), 201

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power is None:
        return jsonify({"error": "Power not found"}), 404

    new_description = request.json.get("description")
    if new_description:
        # Validate the new description
        try:
            power.description = new_description
            db.session.commit()
            return jsonify({"id": power.id, "name": power.name, "description": power.description})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
    else:
        return jsonify({"error": "New description is required"}), 400




if __name__ == '__main__':
    app.run(port=5000)
