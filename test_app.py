import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

# Signup test route
def test_signup_success(client):
    email = 'test2@example.com'
    password = 'password'
    role = 'user'

    response = client.post('/signup', json={'email': email, 'password': password, 'role': role})

    assert response.status_code == 200
    assert response.json['message'] == 'User signed up successfully'


# Login test route
def test_login_success(client):
    email = 'test@example.com'
    password = 'password'
    role = 'user'

    client.post('/login', json={'email': email, 'password': password, 'role': role})

    response = client.post('/login', json={'email': email, 'password': password})

    assert response.status_code == 200
    assert response.json['message'] == 'User logged in successfully'
    assert response.json['data']['role'] == role
    assert response.json['data']['email'] == email

# Display menu test route
def test_display_menu_success(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.json['data']['menu']

# Add dish test route
def test_add_dish_success(client):
    dish_name = 'Test Dish'
    price = 10
    image = 'https://example.com/image.png'
    availability = True

    response = client.post('/menu/add', json={'name': dish_name, 'price': price, 'image': image, 'availability': availability})

    assert response.status_code == 200
    assert response.json['message'] == 'Dish added successfully'

# Remove dish test route
def test_remove_dish_success(client):
    dish_id = 11

    response = client.delete('/menu/remove/{}'.format(dish_id))

    assert response.status_code == 200
    assert response.json['message'] == 'Dish removed successfully'

# Update dish test route
def test_update_dish_success(client):
    dish_id = 1
    new_price = 20

    response = client.put('/menu/update_dish/{}'.format(dish_id), json={'price': new_price})

    assert response.status_code == 200
    assert response.json['message'] == 'Dish updated successfully'

# New order test route
def test_new_order_success(client):
    customer_name = 'Test Customer'
    customer_email = 'test@example.com'
    dish_ids = '1,2,3'

    response = client.post('/order/new', json={'customer_name': customer_name, 'customer_email': customer_email, 'dish_ids': dish_ids})

    assert response.status_code == 200
    assert response.json['message'] == 'Order placed successfully'
    assert response.json['data']['order_id']

# Order update test route
def test_order_update_status(client):
    # Test successful update
    order_id = 4
    status = 'ready'
    data = {'order_id': order_id, 'status': status, 'customer_email':'test@example.com'}

    response = client.put('/order/update_status', json=data)

    assert response.status_code == 200
    assert response.json['message'] == 'Order status updated successfully'


def test_display_orders_success(client):

    response = client.get('/orders/user/test@example.com')

    assert response.status_code == 200
    assert response.json['data']['orders']


