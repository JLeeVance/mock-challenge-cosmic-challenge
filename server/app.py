#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

class Index(Resource):

    def get(self):
        return make_response('<h1>Home</h1>', 200)
    
api.add_resource(Index, '/')

class Scientists(Resource):

    def get(self):
        scientists = [scientist.to_dict(rules = ('-missions',)) for scientist in Scientist.query.all()]

        return make_response(scientists, 200)
    
    def post(self):
        post_data = request.get_json()
        new_scientist = Scientist()

        try:
            for key, value in post_data.items():
                setattr(new_scientist, key, value)

                db.session.add(new_scientist)
                db.session.commit()

            return make_response(new_scientist.to_dict(), 202)

        except:
            return make_response({'errors':['validation errors']}, 400)
        
api.add_resource(Scientists, '/scientists')

class ScientistByID(Resource):

    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if scientist:
            return make_response(scientist.to_dict(), 200)
        else:
            return make_response({'error': 'Scientist not found'}, 404)
    
    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if scientist:
            try:
                patch_data = request.get_json()

                for key, value in patch_data.items():
                    setattr(scientist, key, value)

                    db.session.commit()

                return make_response(scientist.to_dict(), 202)
            except:
                return make_response({'errors':['validation errors']}, 400)
        else:
            return make_response({'error':'Scientist not found'}, 404)
    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()

        if scientist:
            try:
                db.session.delete(scientist)
                db.session.commit()

                return make_response({}, 204)
            except:
                return make_response({'errors':['validation errors']})
        else:
            return make_response({'error':'Scientist not found'}, 404)
        
api.add_resource(ScientistByID, '/scientists/<int:id>')

class Planets(Resource):

    def get(self):
        planets = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]

        return make_response(planets, 200)
    
api.add_resource(Planets, '/planets')

class Missions(Resource):

    def get(self):
        missions = [mission.to_dict() for mission in Mission.query.all()]

        return make_response(missions, 200)
    
    def post(self):

        try:
            new_data = request.get_json()
            new_mission = Mission()

            for key, value in new_data.items():
                setattr(new_mission, key, value)

            db.session.add(new_mission)
            db.session.commit()

            return make_response(new_mission.to_dict(), 201)
        except:
            return make_response({'errors': ['validation errors']}, 400)


api.add_resource(Missions, '/missions')
# @app.route('/')
# def home():
#     return ''


if __name__ == '__main__':
    app.run(port=5555, debug=True)
