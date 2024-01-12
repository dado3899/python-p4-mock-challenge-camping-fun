#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
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

@app.route('/')
def home():
    return ''

class Camper_Route(Resource):
    def get(self):
        all_campers = Camper.query.all()
        dict_campers = []
        for camper in all_campers:
            dict_campers.append(camper.to_dict(rules = ('-signups',)))
        return make_response(dict_campers,200)
    def post(self):
        try:
            data = request.get_json()
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(rules = ('-signups',)), 201)
        except:
            return make_response({ "errors": ["validation errors"] },400)

    
class Camper_by_id_Route(Resource):
    def get(self,id):
        single_camper = Camper.query.filter(Camper.id == id).first()
        if single_camper:
            return make_response(single_camper.to_dict(),200)
        else:
            return make_response({"error": "Camper not found"},404)
    def patch(self,id):
        single_camper = Camper.query.filter(Camper.id == id).first()
        if single_camper:
            try:
                data = request.get_json()
                for attr in data:
                    setattr(single_camper,attr,data[attr])
                db.session.add(single_camper)
                db.session.commit()
                return make_response(single_camper.to_dict(rules = ('-signups',)),202)
            except:
                return make_response({"errors": ["validation errors"]},400)
        else:
            return make_response({"error": "Camper not found"},404)

# {
#   "name": "some name",
#   "age": 10
# }
class Activity_Route(Resource):
    def get(self):
        all_activities = Activity.query.all()
        dict_activities = []
        for activity in all_activities:
            dict_activities.append(activity.to_dict(rules = ('-signups',)))
        return make_response(dict_activities,200)
class Activity_by_id_Route(Resource):
    def delete(self,id):
        single_activity = Activity.query.filter(Activity.id == id).first()
        if single_activity:
            db.session.delete(single_activity)
            db.session.commit()
            return make_response({},204)
        else:
            return make_response({"error": "Activity not found"},404)
class Signup_Route(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_signup = Signup(
                time = data['time'],
                camper_id = data['camper_id'],
                activity_id = data["activity_id"]
            )
            db.session.add(new_signup)
            db.session.commit()
            return make_response(new_signup.to_dict(),201)
        except:
            return make_response({ "errors": ["validation errors"] },400)

api.add_resource(Camper_Route,"/campers")
api.add_resource(Camper_by_id_Route,"/campers/<int:id>")
api.add_resource(Activity_Route,"/activities")
api.add_resource(Activity_by_id_Route,"/activities/<int:id>")
api.add_resource(Signup_Route,'/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
