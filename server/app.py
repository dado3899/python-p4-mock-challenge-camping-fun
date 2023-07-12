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


@app.route('/')
def home():
    return ''

@app.route('/campers', methods = ["GET","POST"])
def allCampers():
    if request.method == "GET":
        all_campers = Camper.query.all()
        dict_campers = []
        for camper in all_campers:
            camper.serialize_only = ("id","name","age")
            dict_campers.append(camper.to_dict())
        return make_response(dict_campers,200)
    if request.method == "POST":
        try:
            data = request.get_json()
            new_camper = Camper(name = data["name"], age = data["age"])
            db.session.add(new_camper)
            db.session.commit()
            new_camper.serialize_only = ("id","name","age")
            return make_response(new_camper.to_dict(),201)
        except:
            return make_response({ "errors": ["validation errors"] },400)

@app.route('/campers/<id>', methods = ["GET","PATCH"])
def oneCamper(id):
    camper = Camper.query.filter(Camper.id==id).first()
    if camper:
        if request.method == "GET":
            return make_response(camper.to_dict(),200)
        if request.method == "PATCH":
            try:
                data = request.get_json()
                for attr in data:
                    setattr(camper, attr, data[attr])
                db.session.add(camper)
                db.session.commit()
                camper.serialize_only = ("id","name","age")
                return make_response(camper.to_dict(),200)
            except:
                return make_response({"errors": ["validation errors"]},400)
    else:
        return make_response({"error": "Camper not found"},400)

@app.route('/activities', methods = ["GET"])
def allActivities():
    if request.method == "GET":
        all_activity = Activity.query.all()
        dict_activity = []
        for activity in all_activity:
            activity.serialize_only = ("id","name","difficulty")
            dict_activity.append(activity.to_dict())
        return make_response(dict_activity,200)

@app.route('/activities/<id>', methods = ["DELETE"])
def oneActivity(id):
    activity = Activity.query.filter(Activity.id == id).first()
    if activity:
        db.session.delete(activity)
        db.session.commit()
        return make_response({},200)
    else:
        return make_response({"error": "Activity not found"},400)

@app.route('/signups', methods = ["POST"])
def signupsRoute():
    if request.method == "POST":
        data = request.get_json()
        camper = Camper.query.filter(Camper.id==data["camper_id"]).first()
        activity = Activity.query.filter(Activity.id == data["activity_id"]).first()
        if camper and activity:
            signup = Signup(time = data["time"], camper=camper, activity=activity)
            db.session.add(signup)
            db.session.commit()
            return make_response(signup.to_dict(),201)
        return make_response({ "errors": ["validation errors"] },400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
