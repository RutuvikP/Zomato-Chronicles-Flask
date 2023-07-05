import json
from flask_cors import CORS
from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Load menu data from menu.json
with open('menu.json', 'r') as f:
    menu = json.load(f)

# Load orders data from orders.json
with open('orders.json', 'r') as f:
    orders = json.load(f)

# Load users data from users.json
with open('users.json', 'r') as f:
    users = json.load(f)

def get_dish_by_id(dish_id):
    for dish in menu:
        if dish['id'] == dish_id:
            return dish
    return None

def update_dish_availability(dish_id, availability):
    dish = get_dish_by_id(dish_id)
    if dish:
        dish['availability'] = availability
        return True
    return False

def get_order_by_id(order_id):
    for order in orders:
        if order['id'] == order_id:
            return order
    
    return None

def add_order(customer_name, dish_ids):
    order_id = len(orders) + 1
    order = {'id': order_id, 'customer_name': customer_name, 'dish_ids': dish_ids, 'status': 'received'}
    orders.append(order)

    # Save updated orders data to orders.json
    with open('orders.json', 'w') as f:
        json.dump(orders, f, indent=4)

    return order_id

def update_order_status(order_id, status):
    for order in orders:
        if order['id'] == order_id:
            order['status'] = status

            # Save updated orders data to orders.json
            with open('orders.json', 'w') as f:
                json.dump(orders, f, indent=4)

            return True
    return False

def get_user_by_email(email):
    for user in users:
        if user['email'] == email:
            return user
    return None

def create_user(email, password, role):
    user_id = len(users) + 1
    user = {'id': user_id, 'email': email, 'password': password, 'role':role}
    users.append(user)

    # Save updated users data to users.json
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

    return user_id

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']
        role = data['role']
        
        # Check if the user with the given email already exists
        with open('users.json', 'r') as f:
            users = json.load(f)
            for user in users:
                if user['email'] == email:
                    return jsonify(error='User with this email already exists')

        # Create a new user
        user_id = len(users) + 1
        user = {'id': user_id, 'email': email, 'password': password, 'role':role}
        users.append(user)

        # Save updated users data to users.json
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

        return jsonify(message='User signed up successfully')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']

        # Check if the user with the given email and password exists
        with open('users.json', 'r') as f:
            users = json.load(f)
            for user in users:
                if user['email'] == email and user['password'] == password:
                    return jsonify(message='User logged in successfully', role=user['role'])

        # If no matching user found, return an error message
        return jsonify(error='Invalid email or password')

# Route for displaying the menu
@app.route('/')
def display_menu():
    return jsonify(menu=menu)

# Route for adding a new dish to the menu
@app.route('/menu/add', methods=['POST'])
def add_dish():
    if request.method == 'POST':
        data = request.get_json()
        dish_id = len(menu) + 1
        dish_name = data['name']
        price = int(data['price'])
        image = data['image']
        availability = data.get('availability', False)
        dish = {'id': dish_id, 'name': dish_name, 'price': price, 'image': image, 'availability': availability}
        menu.append(dish)

        # Save updated menu data to menu.json
        with open('menu.json', 'w') as f:
            json.dump(menu, f, indent=4)

        return jsonify(message='Dish added successfully')

# Route for removing a dish from the menu
@app.route('/menu/remove/<int:dish_id>', methods=['DELETE'])
def remove_dish(dish_id):
    dish = get_dish_by_id(dish_id)
    if dish:
        menu.remove(dish)

        # Save updated menu data to menu.json
        with open('menu.json', 'w') as f:
            json.dump(menu, f, indent=4)

        return jsonify(message='Dish removed successfully')
    else:
        return jsonify(error='Invalid dish ID')

# Route for updating the availability of a dish
@app.route('/menu/update_dish/<int:dish_id>', methods=['PUT'])
def update_dish(dish_id):
    dish = get_dish_by_id(dish_id)
    if dish:
        data = request.get_json()
        if 'price' in data:
            dish['price'] = data['price']
        if 'availability' in data:
            dish['availability'] = data['availability']

        # Save updated menu data to menu.json
        with open('menu.json', 'w') as f:
            json.dump(menu, f, indent=4)

        return jsonify(message='Dish updated successfully')
    else:
        return jsonify(error='Invalid dish ID')


# Route for taking a new order
@app.route('/order/new', methods=['POST'])
def new_order():
    if request.method == 'POST':
        data = request.get_json()
        customer_name = data['customer_name']
        dish_ids = [int(dish_id.strip()) for dish_id in data['dish_ids'].split(',')]

        for dish_id in dish_ids:
            dish = get_dish_by_id(dish_id)
            if not dish or not dish['availability']:
                return jsonify(error='Invalid dish ID or dish not available')

        order_id = add_order(customer_name, dish_ids)
        return jsonify(message='Order placed successfully', order_id=order_id)


# Route for updating the status of an order
@app.route('/order/update_status', methods=['PUT'])
def update_status():
    data = request.get_json()
    order_id = int(data['order_id'])
    status = data['status']
    if update_order_status(order_id, status):
        return jsonify(message='Order status updated successfully')
    else:
        return jsonify(error='Invalid order ID')


# Route for displaying all orders
@app.route('/orders')
def display_orders():
    orders_with_details = []
    for order in orders:
        order_with_details = {}
        order_with_details['id'] = order['id']
        order_with_details['customer_name'] = order['customer_name']
        order_with_details['status'] = order['status']

        # Fetch dish names and calculate total price
        dish_names = [get_dish_by_id(dish_id)['name'] for dish_id in order['dish_ids']]
        total_price = sum([int(get_dish_by_id(dish_id)['price']) for dish_id in order['dish_ids']])

        order_with_details['dishes'] = dish_names
        order_with_details['total_price'] = total_price

        orders_with_details.append(order_with_details)

    return jsonify(orders=orders_with_details)



if __name__ == '__main__':
    app.run(debug=True)
