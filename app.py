from flask import Flask, request, jsonify 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_restful import Resource, Api
from hidden import login
from datetime import datetime

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://gbavxqjy:"+login["password"]+"@ziggy.db.elephantsql.com:5432/gbavxqjy"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Tank(db.Model):
    __tablename__ = "tanks"

    id = db.Column(db.Integer, primary_key = True)
    location = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    percentage_full = db.Column(db.Integer, nullable=False)

class TankSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Tank
        fields = ("id", "location", "lat", "long", "percentage_full")

db.init_app(app)
migrate = Migrate(app, db)

CORS(app) 
api = Api(app)

@app.route("/")
def welcome():   
    return "Welcome!"

profile = {
    "success": True,
    "data": {
        "last_updated": "2/3/2021, 8:48:51 PM", 
        "username": "coolname",
        "role": "Engineer",
        "color": "#3478ff"
    }
}

tank_info = []
tank_id = 0

class Profile(Resource):
    def get(self):
        return profile

    def post(self):
        profile["data"]["last_updated"] = datetime.now().strftime("%c")
        profile["data"]["username"] = request.json['username']
        profile["data"]["role"] = request.json['role']
        profile["data"]["color"] = request.json['color']
        return profile

    def patch(self):
        profile["data"]["last_updated"] = datetime.now().strftime("%c")

        data = (request.json)
        for key in data:
            profile["data"][key] = request.json[key]
        
        return profile

class Data(Resource):
    def get(self):
        tanks = Tank.query.all();
        tanks_json = TankSchema(many = True).dump(tanks)
        return jsonify(tanks_json)


    def post(self):
        newTank = Tank(
            location = request.json["location"],
            long = request.json["long"],
            lat = request.json["lat"],
            percentage_full = request.json["percentage_full"]
        )
        db.session.add(newTank)
        db.session.commit()
        return TankSchema().dump(newTank)

class Data2(Resource):
    def patch(self, id):
        tank = Tank.query.get(id)
        update = request.json

        if "location" in update:
            tank.location = update["location"]
        if "long" in update:
            tank.long = update["long"]
        if "lat" in update: 
            tank.lat = update["lat"]
        if "percentage_full" in update:
            tank.percentage_full = update["percentage_full"]
        
        db.session.commit()
        return TankSchema().dump(tank)


    def delete(self, id):
        tank = Tank.query.get(id)
        db.session.delete(tank)
        db.session.commit()
        return{
            "success": True
        }


api.add_resource(Profile, "/profile")
api.add_resource(Data, "/data")
api.add_resource(Data2, "/data/<int:id>")

if __name__ == '__main__':
    app.run(debug=True,
    port = 3000,
    host = "0.0.0.0"
    )
