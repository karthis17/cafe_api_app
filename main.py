import os
import random

from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafe = db.session.query(Cafe).all()
    random_cafe = random.choice(cafe)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price
    })


@app.route("/all")
def get_all_cafe():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafe={cafe.id: {"id": cafe.id,
                                   "name": cafe.name,
                                   "map_url": cafe.map_url,
                                   "img_url": cafe.img_url,
                                   "location": cafe.location,
                                   "seats": cafe.seats,
                                   "has_toilet": cafe.has_toilet,
                                   "has_wifi": cafe.has_wifi,
                                   "has_sockets": cafe.has_sockets,
                                   "can_take_calls": cafe.can_take_calls,
                                   "coffee_price": cafe.coffee_price} for cafe in cafes})


@app.route("/search")
def get_cafe_at_location():
    query_location = request.form.get("loc")
    cafes = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafes:
        return jsonify(cafe=cafes.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


# HTTP POST - Create Record

@app.route("/add", methods=["POST", "GET"])
def add_cafe():
    new_cafe = Cafe(
        name=request.args.get("cafe"),
        map_url=request.args.get("map_url"),
        img_url=request.args.get("img_url"),
        location=request.args.get("loc"),
        has_sockets=bool(request.args.get("sockets")),
        has_toilet=bool(request.args.get("toilet")),
        has_wifi=bool(request.args.get("wifi")),
        can_take_calls=bool(request.args.get("calls")),
        seats=request.args.get("seats"),
        coffee_price=request.args.get("coffee_price"),
    )
    db.session.add(new_cafe):
    db.session.commit()
    


# HTTP PUT/PATCH - Update Record

@app.route("/user-update/<id_to_update>", methods=["GET", "PATCH"])
def update_cafe(id_to_update):
    new_price = request.args.get("price")
    cafe = db.session.query(Cafe).get(id_to_update)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(sucess="Successfully price was updated.")
    else:
        return jsonify(unsuccess="Please check the id it supposed be not exist.")


# HTTP DELETE - Delete Record
@app.route("/delete-report/<_id_>", methods=["POST"])
def report_to_delete(_id_):
    cafe = db.session.query(Cafe).get(_id_)
    api_secret_key = "!@#$%^&*()"
    if cafe:
        if request.args.get("secret_key") == api_secret_key:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(sucess="Successfully price was deleted.")
        return jsonify(failed="wrong security key go back.")
    else:
        return jsonify(unsuccess="Please check the id it supposed be not exist.")


if __name__ == '__main__':
    app.run()
