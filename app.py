import os
import sqlite3
from flask import Flask, g, send_from_directory, jsonify, request

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'data.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Create your table if it doesn't exist, and insert sample data."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    ''')
    # Optional: seed data if empty
    cursor.execute('SELECT COUNT(*) FROM items')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO items (name) VALUES ('First item'), ('Second item')")
    conn.commit()

# Initialize DB at startup
with app.app_context():
    init_db()

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/service-worker.js')
def sw():
    response = send_from_directory('static', 'service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/api/items', methods=['GET'])
def get_items():
    """Return all items as JSON."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM items")
    rows = cursor.fetchall()
    data = [{'id': row[0], 'name': row[1]} for row in rows]
    return jsonify(data)

@app.route('/api/additem', methods=['POST'])
def add_item():
    """Insert a new item into the DB and return success or updated list."""
    conn = get_db()
    cursor = conn.cursor()

    # We expect JSON data: { "name": "some text" }
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'No item name provided'}), 400
    
    name = data['name']
    cursor.execute("INSERT INTO items (name) VALUES (?)", (name,))
    conn.commit()

    # Option 1: Return just success message
    # return jsonify({"message": "Item added successfully"})

    # Option 2: Return updated list so the client can refresh easily
    cursor.execute("SELECT id, name FROM items")
    rows = cursor.fetchall()
    items = [{'id': row[0], 'name': row[1]} for row in rows]
    return jsonify(items)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)