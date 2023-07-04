import json
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Load menu data from menu.json
with open('menu.json', 'r') as f:
    menu = json.load(f)

# Load orders data from orders.json
with open('orders.json', 'r') as f:
    orders = json.load(f)

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

# Route for displaying the menu
@app.route('/')
def display_menu():
    return render_template('menu.html', menu=menu)

# Route for adding a new dish to the menu
@app.route('/menu/add', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        dish_id = len(menu) + 1
        dish_name = request.form['name']
        price = int(request.form['price'])
        availability = request.form.get('availability') == 'on'
        dish = {'id': dish_id, 'name': dish_name, 'price': price, 'availability': availability}
        menu.append(dish)

        # Save updated menu data to menu.json
        with open('menu.json', 'w') as f:
            json.dump(menu, f, indent=4)

        return redirect('/')
    
    return render_template('add_dish.html')

# Route for removing a dish from the menu
@app.route('/menu/remove/<int:dish_id>')
def remove_dish(dish_id):
    dish = get_dish_by_id(dish_id)
    if dish:
        menu.remove(dish)

        # Save updated menu data to menu.json
        with open('menu.json', 'w') as f:
            json.dump(menu, f, indent=4)

    return redirect('/')

# Route for updating the availability of a dish
@app.route('/menu/update_availability/<int:dish_id>/<string:availability>')
def update_availability(dish_id, availability):
    if availability.lower() == 'true':
        availability = False
    else:
        availability = True
    update_dish_availability(dish_id, availability)

    # Save updated menu data to menu.json
    with open('menu.json', 'w') as f:
        json.dump(menu, f, indent=4)

    return redirect('/')

# Route for taking a new order
@app.route('/order/new', methods=['GET', 'POST'])
def new_order():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        dish_ids = [int(dish_id.strip()) for dish_id in request.form['dish_ids'].split(',')]
        print(dish_ids)
        
        for dish_id in dish_ids:
            dish = get_dish_by_id(dish_id)
            print(f'Dish ID: {dish_id}, Dish: {dish}')
            if not dish or not dish['availability']:
                return 'Invalid dish ID or dish not available'
        
        order_id = add_order(customer_name, dish_ids)
        return redirect('/orders')
    
    return render_template('new_order.html', menu=menu)

# Route for updating the status of an order
@app.route('/order/update_status', methods=['POST'])
def update_status():
    order_id = int(request.form['order_id'])
    status = request.form['status']
    if update_order_status(order_id, status):
        return redirect('/orders')
    return 'Invalid order ID'

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
        total_price = sum([get_dish_by_id(dish_id)['price'] for dish_id in order['dish_ids']])
        
        order_with_details['dishes'] = dish_names
        order_with_details['total_price'] = total_price
        
        orders_with_details.append(order_with_details)

    return render_template('orders.html', orders=orders_with_details)


if __name__ == '__main__':
    app.run(debug=True)
