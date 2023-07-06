import json
from flask_cors import CORS
from flask import Flask, request, jsonify
import ssl
import pymongo
from pymongo import MongoClient
from bson import json_util

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://rutuvik:patil@cluster0.yalls5i.mongodb.net/flavorfusion?retryWrites=true&w=majority",ssl=True,ssl_cert_reqs=ssl.CERT_NONE)
db = client.get_database("flavorfusion")
menu_collection = db.menu
orders_collection = db.orders
users_collection = db.users

def get_dish_by_id(dish_id):
    return menu_collection.find_one({"id": dish_id})

def update_dish_availability(dish_id, availability):
    result = menu_collection.update_one({"id": dish_id}, {"$set": {"availability": availability}})
    return result.modified_count > 0

def get_order_by_id(order_id):
    return orders_collection.find_one({"id": order_id})

def add_order(customer_name, dish_ids, customer_email):
    order_id = orders_collection.count_documents({}) + 1
    order = {'id': order_id, 'customer_name': customer_name, 'customer_email':customer_email, 'dish_ids': dish_ids, 'status': 'received'}
    orders_collection.insert_one(order)
    return order_id

def update_order_status(order_id, status):
    result = orders_collection.update_one({"id": order_id}, {"$set": {"status": status}})
    return result.modified_count > 0

def get_user_by_email(email):
    return users_collection.find_one({"email": email})

def create_user(email, password, role):
    user_id = users_collection.count_documents({}) + 1
    user = {'id': user_id, 'email': email, 'password': password, 'role': role}
    users_collection.insert_one(user)
    return user_id

def generate_response(data=None, message=None, error=None, status_code=200):
    response = {'data': data, 'message': message, 'error': error}
    return jsonify(response), status_code

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']
        role = data['role']
        
        # Check if the user with the given email already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return generate_response(error='User with this email already exists', status_code=400)

        # Create a new user
        user_id = create_user(email, password, role)
        return generate_response(message='User signed up successfully')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']

        # Check if the user with the given email and password exists
        user = get_user_by_email(email)
        if user and user['password'] == password:
            return generate_response(message='User logged in successfully', data={'role': user['role'],'email':user['email']})

        # If no matching user found, return an error message
        return generate_response(error='Invalid email or password', status_code=401)

@app.route('/')
def display_menu():
    menu = list(menu_collection.find())
    menu_json = json.dumps(menu, default=json_util.default)
    menu_dict = json.loads(menu_json)
    return generate_response(data={'menu': menu_dict})

@app.route('/menu/add', methods=['POST'])
def add_dish():
    if request.method == 'POST':
        data = request.get_json()
        dish_id = menu_collection.count_documents({}) + 1
        dish_name = data['name']
        price = int(data['price'])
        image = data['image']
        availability = data.get('availability', False)
        dish = {'id': dish_id, 'name': dish_name, 'price': price, 'image': image, 'availability': availability}
        menu_collection.insert_one(dish)
        return generate_response(message='Dish added successfully')

@app.route('/menu/remove/<int:dish_id>', methods=['DELETE'])
def remove_dish(dish_id):
    result = menu_collection.delete_one({"id": dish_id})
    if result.deleted_count > 0:
        return generate_response(message='Dish removed successfully')
    else:
        return generate_response(error='Invalid dish ID', status_code=400)

@app.route('/menu/update_dish/<int:dish_id>', methods=['PUT'])
def update_dish(dish_id):
    dish = get_dish_by_id(dish_id)
    if dish:
        data = request.get_json()
        updates = {}
        if 'price' in data:
            updates['price'] = int(data['price'])
        if 'availability' in data:
            updates['availability'] = data['availability']
        menu_collection.update_one({"id": dish_id}, {"$set": updates})
        return generate_response(message='Dish updated successfully')
    else:
        return generate_response(error='Invalid dish ID', status_code=400)

@app.route('/order/new', methods=['POST'])
def new_order():
    if request.method == 'POST':
        data = request.get_json()
        customer_name = data['customer_name']
        customer_email = data['customer_email']
        dish_ids = [int(dish_id.strip()) for dish_id in data['dish_ids'].split(',')]

        for dish_id in dish_ids:
            dish = get_dish_by_id(dish_id)
            if not dish or not dish['availability']:
                return generate_response(error='Invalid dish ID or dish not available', status_code=400)

        order_id = add_order(customer_name, dish_ids, customer_email)
        return generate_response(message='Order placed successfully', data={'order_id': order_id})

@app.route('/order/update_status', methods=['PUT'])
def update_status():
    data = request.get_json()
    order_id = int(data['order_id'])
    status = data['status']
    if update_order_status(order_id, status):
        return generate_response(message='Order status updated successfully')
    else:
        return generate_response(error='Invalid order ID', status_code=400)

@app.route('/orders')
def display_orders():
    orders = list(orders_collection.find())
    orders_with_details = []
    for order in orders:
        order_with_details = {}
        order_with_details['id'] = order['id']
        order_with_details['customer_name'] = order['customer_name']
        order_with_details['status'] = order['status']

        dish_names = []
        total_price = 0
        for dish_id in order['dish_ids']:
            dish = get_dish_by_id(dish_id)
            if dish:
                dish_names.append(dish['name'])
                total_price += dish['price']

        order_with_details['dishes'] = dish_names
        order_with_details['total_price'] = total_price

        orders_with_details.append(order_with_details)

    return generate_response(data={'orders': orders_with_details})

if __name__ == '__main__':
    app.run(debug=True)
