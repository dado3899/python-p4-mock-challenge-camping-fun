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

class getAllCampers(Resource):
    def get(self):
        campers = Camper.query.all()
        return [camper.to_dict(rules=('-signups',)) for camper in campers],200
    def post(self):
        try:
            data= request.get_json()
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            return new_camper.to_dict(rules=("-signups",)),201
        except Exception as e:
            print(e)
            return { "errors": ["validation errors"] },400
    
class getOneCamper(Resource):
    def get(self,id):
        camper = Camper.query.filter(Camper.id == id).first()
        if(camper):
            return camper.to_dict(),200
        else:
            return {
                "error": "Camper not found"
            }, 404
        
    def patch(self,id):
        camper = Camper.query.filter(Camper.id == id).first()
        if(camper):
            try:
                data= request.get_json()
                for key in data:
                    setattr(camper,key,data[key])
                db.session.add(camper)
                db.session.commit()
                return camper.to_dict(),202
            except Exception as e:
                print(e)
                return {"errors": ["validation errors"]}, 400
        else:
            return {
                "error": "Camper not found"
            }, 404

class getAllActivities(Resource):
    def get(self):
        activities = Activity.query.all()
        return [activity.to_dict(rules=('-signups',)) for activity in activities],200

class getOneActivity(Resource):
    def delete(self,id):
        activity = Activity.query.filter(Activity.id == id).first()
        if(activity):
            signups = Signup.query.filter(Signup.activity_id == activity.id).all()
            for signup in signups:
                db.session.delete(signup)
            db.session.delete(activity)
            db.session.commit()
            return {},204
        else:
            return {
                "error": "Activity not found"
            }, 404
        
class getAllSignups(Resource):
    def post(self):
        try:
            data= request.get_json()
            signup = Signup(
                time = data['time'],
                camper_id = data['camper_id'],
                activity_id = data['activity_id']
            )
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(),201
        except Exception as e:
            return { "errors": ["validation errors"] },400


api.add_resource(getOneActivity,'/activities/<id>')
api.add_resource(getAllActivities,'/activities')
api.add_resource(getOneCamper, '/campers/<id>')
api.add_resource(getAllCampers,'/campers')
api.add_resource(getAllSignups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
