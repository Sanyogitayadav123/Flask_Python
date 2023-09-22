from flask import Flask , request, jsonify,render_template ,redirect, url_for  # Import redirect and url_for
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token
import bcrypt 
from datetime import datetime
from blog import blog_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'ASDFGHJKLMNBVCZXQWERTYUIOP'  # Change this to a secure secret key
jwt = JWTManager(app)
app.register_blueprint(blog_bp, url_prefix='/blog')

@app.route('/')
def hello_world():
    # return '<p>Hello World !!</p>'
      return render_template('home.html')

@app.route('/register')
def register_user():
     return render_template('register.html')

@app.route('/login')
def login_user():
    return render_template('login.html')


@app.route('/productTable', endpoint='productTable') 
def product_table():
    return render_template('productTable.html')

@app.route('/update-blog')
def update_blog_page():
    return render_template('update-blog.html')

@app.route('/add-blog')
def add_blog_page():
    return render_template('add-blog.html')


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="test_python_db"
    )

def ensure_last_login_column_exists(cursor):
    # Check if the 'last_login' column exists in the 'users' table
    cursor.execute("SHOW COLUMNS FROM users LIKE 'last_login'")
    if cursor.fetchone() is None:
        # 'last_login' column does not exist, so add it
        cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")


 
@app.route('/register', methods=['POST'])
def register():
  if request.method == 'POST':
    if request.content_type == 'application/json':
        # Data is sent as JSON
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        mobile = data.get('mobile')
        password = data.get('password')
    elif request.form:
        # Data is sent as form data
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
    else:
        return jsonify({'error': 'Invalid request data'})
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Hash the password before inserting it into the database
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Define the SQL query to insert data into the database
        sql = "INSERT INTO users (name, email, mobile, password) VALUES (%s, %s, %s, %s)"
        values = (name, email, mobile, hashed_password)  # Store the hashed password

        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('login'))
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.content_type == 'application/x-www-form-urlencoded':
        # Form submission
        email = request.form['email']
        password = request.form['password']
    elif request.content_type == 'application/json':
        # JSON data
        data = request.get_json()
        email = data.get('email', '')  # Using get() to provide a default value
        password = data.get('password', '')  # Using get() to provide a default value
    else:
        return jsonify({'error': 'Unsupported content type'})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        ensure_last_login_column_exists(cursor)

        # Define the SQL query to check if the user exists and the password matches
        sql = "SELECT * FROM users WHERE email = %s"
        cursor.execute(sql, (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user[3]  # Assuming the password is stored in the fourth column
            # Verify the password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                # Update the last_login timestamp
                last_login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_sql = "UPDATE users SET last_login = %s WHERE email = %s"
                cursor.execute(update_sql, (last_login_time, email))
                conn.commit()

                # Generate an access token
                # access_token = create_access_token(identity=email)
                # return jsonify({'success': 'Login successful', 'access_token': access_token})
                return redirect(url_for('productTable'))

            else:
                return jsonify({'error': 'Invalid credentials'})
        else:
            return jsonify({'error': 'User not found'})

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080) 
