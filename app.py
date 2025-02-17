import os
import sqlite3
from flask import Flask, g, send_from_directory, jsonify

app = Flask(__name__)

# Path to your SQLite database file
DATABASE = os.path.join(os.path.dirname(__file__), 'data.db')

# ----------------------------
# 1) Database helper functions
# ----------------------------
def get_db():
    """Get a SQLite connection from the 'g' context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_db(exception):
    """Close DB connection at the end of request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Create your 'items' table if not exists, and optionally seed data."""
    conn = get_db()
    cursor = conn.cursor()
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    ''')
    # Seed data if table empty
    cursor.execute('SELECT COUNT(*) FROM items')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO items (name) VALUES ('First item'), ('Second item')")
    conn.commit()

# ----------------------------
# 2) Run DB init before app starts
# ----------------------------
with app.app_context():
    init_db()

# ----------------------------
# 3) Routes
# ----------------------------
@app.route('/')
def home():
    """Serve the static index.html from the 'static' folder."""
    return app.send_static_file('index.html')

@app.route('/service-worker.js')
def sw():
    """Serve service-worker.js from 'static' but at the root path."""
    response = send_from_directory('static', 'service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/api/items')
def get_items():
    """Example API endpoint returning items from the DB as JSON."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM items")
    rows = cursor.fetchall()
    data = [{'id': row[0], 'name': row[1]} for row in rows]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)