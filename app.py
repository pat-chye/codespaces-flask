# app.py
import os
import sqlite3
from flask import Flask, g, jsonify

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(__file__), 'data.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Create a simple table if not exists, and insert sample data."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('SELECT COUNT(*) FROM items')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO items (name) VALUES ('First item'), ('Second item'), ('Third item')")
    conn.commit()

@app.before_first_request
def setup():
    init_db()

# Serve index.html as the homepage from /static/index.html
@app.route('/')
def home():
    return app.send_static_file('index.html')

# API endpoint to get items in JSON
@app.route('/api/items')
def get_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM items")
    rows = cursor.fetchall()
    # Convert to a list of dicts for easy JSON serialization
    items = []
    for row in rows:
        items.append({'id': row[0], 'name': row[1]})
    return jsonify(items)

# Service Worker route if you want it at root (optional)
@app.route('/service-worker.js')
def sw():
    response = app.send_static_file('service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

if __name__ == '__main__':
    # Typical run command in Codespaces:
    # flask --debug run --host=0.0.0.0 --port=5000
    app.run(debug=True, host='0.0.0.0', port=5000)