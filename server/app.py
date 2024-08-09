#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


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

class All_Campers(Resource):
    def get(self):
        ac = Camper.query.all()
        return [camper.to_dict(rules=('-signups',)) for camper in ac],200
    def post(self):
        try:
            data = request.get_json()
            camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(rules=('-signups',)),200
        except Exception as e:
            print(e)
            return { "errors": ["validation errors"] },400

    
class One_Camper(Resource):
    def get(self,id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            return camper.to_dict(),200
        else:
            return {
                "error": "Camper not found"
            },404
    def patch(self,id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            try:
                data = request.get_json()
                for key in data:
                    setattr(camper,key,data[key])
                db.session.add(camper)
                db.session.commit()
                return camper.to_dict(rules=('-signups',)),202
            except Exception as e:
                print(e)
                return {
                        "errors": ["validation errors"]
                    },400
        else:
            return {
                "error": "Camper not found"
            },404
    
class All_Activities(Resource):
    def get(self):
        aa = Activity.query.all()
        r_l = []
        for activity in aa:
            r_l.append(activity.to_dict(rules=('-signups',)))
        return r_l,200

class One_Activity(Resource):
    def delete(self,id):
        activity = Activity.query.filter(Activity.id==id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return {},204
        else:
            return {
                    "error": "Activity not found"
                    }, 404
class All_Signups(Resource):
    def post(self):
        try:
            data = request.get_json()
            su = Signup(
                time = data['time'],
                camper_id = data['camper_id'],
                activity_id = data['activity_id']
            )
            db.session.add(su)
            db.session.commit()
            return su.to_dict(),201
        except Exception as e:
            print(e)
            return  { "errors": ["validation errors"] },400

api.add_resource(All_Signups,'/signups')
api.add_resource(All_Campers,'/campers')
api.add_resource(One_Camper,'/campers/<int:id>')
api.add_resource(All_Activities, '/activities')
api.add_resource(One_Activity,'/activities/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
