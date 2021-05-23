from flask import Flask, abort, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError


import json
with open("secret.json") as f:
    SECRET = json.load(f)

DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
    user=SECRET["user"],
    password=SECRET["password"],
    host=SECRET["host"],
    port=SECRET["port"],
    db=SECRET["db"])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material = db.Column(db.String(50))
    price = db.Column(db.Integer)

    def int(self, material, price):
        self.material = material
        self.price = price


class DeviceSchema(ma.Schema):
    class Meta:
        fields = ("price", "material")


device_schema = DeviceSchema()
devices_schema = DeviceSchema(many=True)


@app.route("/device", methods=["GET"])
def get_devices():
    all_device = Device.query.all()
    result = devices_schema.dump(all_device)
    if not result:
        abort(404)
    return jsonify({'user_schema': result})


@app.route("/device/<id>", methods=["GET"])
def get_device(id):
    device = Device.query.get(id)
    if not device:
        abort(404)
    return device_schema.jsonify(device)


@app.route("/device", methods=["POST"])
def add_device():
    try:
        info_about_class = DeviceSchema().load(request.json)
        device = Device(**info_about_class)

    except ValidationError:
        abort(400)
    db.session.add(device)
    db.session.commit()
    return device_schema.jsonify(device)


@app.route("/device/<id>", methods=["PUT"])
def device_update(id):
    device = Device.query.get(id)
    if not device:
        abort(404)
    device.price = request.json["price"]
    device.material = request.json["material"]
    db.session.commit()
    return jsonify(success=True)


@app.route("/device/<id>", methods=["DELETE"])
def device_delete(id):
    device = Device.query.get(id)
    if not device:
        abort(404)
    db.session.delete(device)
    db.session.commit()
    return jsonify(success=True)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host="127.0.0.1")