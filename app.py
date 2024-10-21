from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'fghfjknrglsnvldnswer3432efbdaw3%##$r23d'

# Database connection setup
def create_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='host',  # Your MySQL username
        password='root',  # Your MySQL password
        database='rithi'  # Your database name
    )
    return connection

@app.route('/')
def home():
    return render_template('customer_login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Admin login credentials hardcoded
        if username == 'admin' and password == 'adminpass':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return 'Invalid Admin credentials, please try again.'
    
    return render_template('admin_login.html')

@app.route('/consumer-login', methods=['GET', 'POST'])
def consumer_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database and validate credentials
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        consumer = cursor.fetchone()  # Fetch the user data from the database

        if consumer and consumer['password'] == password:
            session['consumer_logged_in'] = True
            session['username'] = username
            print(f"Logged in as {username}")  # Debug print for testing
            return redirect(url_for('consumer_dashboard'))
        else:
            return 'Invalid Consumer credentials, please try again.'

    return render_template('customer_login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database
        conn = create_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists, please choose a different one.', 'error')
            return redirect(url_for('signup'))

        # Insert new user into the database
        insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(insert_query, (username, password))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Registration successful, please login.', 'success')
        return redirect(url_for('consumer_login'))

    return render_template('signup.html')

@app.route('/consumer_logout')
def consumer_logout():
    session.pop('consumer_logged_in', None)
    session.pop('username', None)
    return redirect(url_for('consumer_login'))



@app.route('/consumer-dashboard')
def consumer_dashboard():
    if not session.get('consumer_logged_in'):
        return redirect(url_for('consumer_login'))
    return render_template('customer_dashboard.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    # Connect to the database to fetch orders
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to get all orders
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', orders=orders)
@app.route('/update_stock/<int:order_id>', methods=['POST'])
def update_stock(order_id):
    new_quantity = request.form.get('new_quantity')

    conn = create_connection()
    cursor = conn.cursor()

    update_query = "UPDATE orders SET stock_level = %s WHERE id = %s"
    cursor.execute(update_query, (new_quantity, order_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard'))




@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route('/about')
def about():
    return 'hello'

@app.route('/building_products')
def building_products():
    print(f"Session: {session.get('consumer_logged_in')}")  # Check if session is set
    if not session.get('consumer_logged_in'):
        return redirect(url_for('consumer_login'))
    return render_template('building_products.html')



# Product routes
@app.route('/product_1')
def product_1():
    return render_template('product1.html')  # Make sure this file exists

@app.route('/product_2')
def product_2():
    return "hello"

@app.route('/product_3')
def product_3():
    return "hello"

@app.route('/product_4')
def product_4():
    return "hello"

@app.route('/product_5')
def product_5():
    return "hello"
@app.route('/orders')
def  orders():
    return "hello"
@app.route('/admin_logout')
def admin_logout():
    return "hello"

@app.route('/submit_order', methods=['POST'])
def submit_order():
    # Safely get form data using .get()
    quantity = request.form.get('quantity')
    location = request.form.get('location')
    preferred_delivery_time = request.form.get('time')

    # Ensure that quantity is provided
    if not quantity:
        flash('Quantity is missing.', 'error')
        return render_template("suk.html")

    try:
        # Connect to the database
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        # Check the current stock level (assuming you're tracking stock globally, not per product)
        cursor.execute("SELECT stock_level FROM orders WHERE id = %s", (1,))  # Assuming id = 1 for a general product
        product = cursor.fetchone()

        if product:
            print(f"Stock Level Found: {product['stock_level']}")  # Debugging line

        # If the product is found and there is enough stock
        if product and product['stock_level'] is not None and product['stock_level'] >= int(quantity):
            new_stock_level = product['stock_level'] - int(quantity)

            # Update the stock level
            update_query = "UPDATE orders SET stock_level = %s WHERE id = %s"
            cursor.execute(update_query, (new_stock_level, 1))  # Update the stock for the product with id = 1

            # Insert the order details into the orders table
            insert_query = """
            INSERT INTO orders (quantity, location, delivery_time) 
            VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (quantity, location, preferred_delivery_time))
            conn.commit()

            flash('Order submitted successfully!', 'success')
        else:
            # Handle the case where there is insufficient stock or the product does not exist
            flash('Insufficient stock to fulfill the order.', 'error')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        print(f"Error occurred: {str(e)}")  # Debugging line
    finally:
        cursor.close()
        conn.close()

    return render_template("suk.html")

@app.route('/create_order', methods=['POST'])
def create_order():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity')

    # Connect to the database
    conn = create_connection()
    cursor = conn.cursor()

    # Insert the new order with default status 'pending'
    insert_query = "INSERT INTO orders (product_id, quantity) VALUES (%s, %s)"
    cursor.execute(insert_query, (product_id, quantity))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('orders_page'))

@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    status = request.form.get('status')

    conn = create_connection()
    cursor = conn.cursor()

    update_query = "UPDATE orders SET status = %s WHERE id = %s"
    cursor.execute(update_query, (status, order_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('admin_dashboard'))




if __name__ == '__main__':
    app.run(debug=True)
