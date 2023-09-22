from flask import Flask , request, jsonify,render_template
import mysql.connector
from flask_jwt_extended import JWTManager, create_access_token
import bcrypt 
from datetime import datetime


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'ASDFGHJKLMNBVCZXQWERTYUIOP'  # Change this to a secure secret key
jwt = JWTManager(app)

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
        data = request.form
        name = data['name']
        email = data['email']
        mobile = data['mobile']
        password = data['password']
        
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
            print(values)
        
            return jsonify({'success': 'Successful registration'})
        except Exception as e:
          print("Error:", e)  # Print the error message for debugging
    return jsonify({'error': 'An error occurred during registration'})



@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data['email']
        password = data['password']

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
                    access_token = create_access_token(identity=email)
                    return jsonify({'success': 'Login successful', 'access_token': access_token})
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
 app.run(debug=True)