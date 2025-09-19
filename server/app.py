#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def get_restaurants():
    restaurants=[]
    for restaurant in Restaurant.query.all():
        restaurant_dict=restaurant.to_dict()
        restaurants.append(restaurant_dict)
    response=make_response(restaurants, 200,
                           {'Content-Type':"application/json"})
    return response

@app.route('/restaurants/<int:id>', methods=["GET", "DELETE"])

def restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)

    if request.method == "GET":
        # Include restaurant_pizzas only for single restaurant
        restaurant_dict = restaurant.to_dict()
        restaurant_dict["restaurant_pizzas"] = [
            rp.to_dict() for rp in restaurant.restaurant_pizzas
        ]
        return make_response(restaurant_dict, 200)

    if request.method == "DELETE":
        # Delete associated RestaurantPizza first if no cascade
        for rp in restaurant.restaurant_pizzas:
            db.session.delete(rp)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)

    

    
@app.route('/pizzas', methods=["GET"])
def get_pizzas():
    pizzas=[pizza.to_dict(only=("id", "name", "ingredients")) for pizza in Pizza.query.all()]
    
    response=make_response(pizzas, 200,
                           {'Content-Type':"application/json"})
    return response
@app.route('/restaurant_pizzas', methods=["POST"])
def post():
    data = request.get_json()
    
    pizza = Pizza.query.get(data.get("pizza_id"))
    restaurant = Restaurant.query.get(data.get("restaurant_id"))
    
    if not pizza or not restaurant:
        return make_response({"errors": ["validation errors"]}, 400)
    
    try:
        restaurant_pizza = RestaurantPizza(
            price=data.get("price"),
            pizza_id=pizza.id,
            restaurant_id=restaurant.id
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
    except ValueError:
        # Always return the expected "validation errors" for the test
        return make_response({"errors": ["validation errors"]}, 400)
    
    return make_response(restaurant_pizza.to_dict(), 201)
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
