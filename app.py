#!/usr/bin/python
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn

def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                country TEXT NOT NULL
            );
        ''')
        conn.commit()
        print("User table created successfully")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, phone, address, country) VALUES (?, ?, ?, ?, ?)",
                    (user['name'], user['email'], user['phone'], user['address'], user['country']))
        conn.commit()
        inserted_user = get_user_by_id(cur.lastrowid)
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error inserting user: {e}")
    finally:
        conn.close()
    return inserted_user

def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()

        # Convert row objects to dictionary
        for i in rows:
            user = {}
            user["user_id"] = i["user_id"]
            user["name"] = i["name"]
            user["email"] = i["email"]
            user["phone"] = i["phone"]
            user["address"] = i["address"]
            user["country"] = i["country"]
            users.append(user)
    except sqlite3.Error as e:
        print(f"Error retrieving users: {e}")
    finally:
        conn.close()
    return users

def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        if row:
            # Convert row object to dictionary
            user["user_id"] = row["user_id"]
            user["name"] = row["name"]
            user["email"] = row["email"]
            user["phone"] = row["phone"]
            user["address"] = row["address"]
            user["country"] = row["country"]
    except sqlite3.Error as e:
        print(f"Error retrieving user by ID: {e}")
    finally:
        conn.close()
    return user

def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET name = ?, email = ?, phone = ?, address = ?, country = ?
            WHERE user_id = ?
        """, (user["name"], user["email"], user["phone"], user["address"], user["country"], user["user_id"]))
        conn.commit()
        updated_user = get_user_by_id(user["user_id"])
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error updating user: {e}")
    finally:
        conn.close()
    return updated_user

def delete_user(user_id):
    message = {}
    try:
        conn = connect_to_db()
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        message["status"] = "User deleted successfully"
    except sqlite3.Error as e:
        conn.rollback()
        message["status"] = f"Cannot delete user: {e}"
    finally:
        conn.close()
    return message

@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify(get_users())

@app.route('/api/users/<int:user_id>', methods=['GET'])
def api_get_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/users/add', methods=['POST'])
def api_add_user():
    user = request.get_json()
    inserted_user = insert_user(user)
    return jsonify(inserted_user), 201

@app.route('/api/users/update', methods=['PUT'])
def api_update_user():
    user = request.get_json()
    updated_user = update_user(user)
    if updated_user:
        return jsonify(updated_user)
    else:
        return jsonify({'error': 'User not found or update failed'}), 400

@app.route('/api/users/delete/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    result = delete_user(user_id)
    if 'successfully' in result.get('status', ''):
        return jsonify(result)
    else:
        return jsonify(result), 400


if __name__ == "__main__":
    # Uncomment the next line if you need to recreate the database table
    # create_db_table()
    app.run(debug=True)

