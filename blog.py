from flask import Blueprint, request, jsonify ,render_template,redirect,url_for
import mysql.connector

# Create a Flask Blueprint for the blog routes
blog_bp = Blueprint("blog", __name__)


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="test_python_db"
    )

# API route for creating a blog post


@blog_bp.route('/create', methods=['POST'])
def create_blog():
    if request.content_type == 'application/json':
        # Handle JSON data
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
    elif request.form:
        # Handle form data
        title = request.form.get('title')
        content = request.form.get('content')
    else:
        # Handle unsupported content type
        return jsonify({'error': 'Unsupported content type'}), 400

    if title and content:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Define the SQL query to insert data into the 'blog' table
            insert_sql = "INSERT INTO blog (title, content) VALUES (%s, %s)"
            values = (title, content)

            cursor.execute(insert_sql, values)
            conn.commit()

            cursor.close()
            conn.close()

            return redirect(url_for('productTable'))

            # return jsonify({'success': 'Blog created successfully', 'data': values}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Title and content are required'}), 400



# API route for getting all blogs
@blog_bp.route('/get-all', methods=['GET'])
def get_all_blogs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Define the SQL query to retrieve all blog posts
        select_all_sql = "SELECT * FROM blog"

        cursor.execute(select_all_sql)
        blogs = cursor.fetchall()

        cursor.close()
        conn.close()

        # Convert the list of blog posts to a list of dictionaries for JSON response
        blog_list = []
        for blog in blogs:
            blog_dict = {
                'id': blog[0],
                'title': blog[1],
                'content': blog[2]
            }
            blog_list.append(blog_dict)

        return jsonify({'blogs': blog_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API route for getting a single blog by ID
@blog_bp.route('/get/<int:blog_id>', methods=['GET'])
def get_blog_by_id(blog_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Define the SQL query to retrieve a blog post by its ID
        select_blog_sql = "SELECT * FROM blog WHERE id = %s"
        cursor.execute(select_blog_sql, (blog_id,))
        blog = cursor.fetchone()

        cursor.close()
        conn.close()

        if blog:
            # Convert the retrieved blog post to a dictionary for JSON response
            blog_dict = {
                'id': blog[0],
                'title': blog[1],
                'content': blog[2]
            }
            return jsonify({'blog': blog_dict}), 200
        else:
            return jsonify({'error': 'Blog not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API route for updating a single blog by ID
@blog_bp.route('/update/<int:blog_id>', methods=['PUT'])
def update_blog_by_id(blog_id):
    data = request.get_json()
    new_title = data.get('title')
    new_content = data.get('content')

    if new_title and new_content:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Define the SQL query to update a blog post by its ID
            update_blog_sql = "UPDATE blog SET title = %s, content = %s WHERE id = %s"
            values = (new_title, new_content, blog_id)

            cursor.execute(update_blog_sql, values)
            conn.commit()

            cursor.close()
            conn.close()

            # return jsonify({'success': 'Blog updated successfully'}), 200
            return redirect(url_for('productTable'))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Title and content are required'}), 400


# API route for deleting a single blog by ID
@blog_bp.route('/delete/<int:blog_id>', methods=['DELETE'])
def delete_blog_by_id(blog_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Define the SQL query to delete a blog post by its ID
        delete_blog_sql = "DELETE FROM blog WHERE id = %s"
        cursor.execute(delete_blog_sql, (blog_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': 'Blog deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
