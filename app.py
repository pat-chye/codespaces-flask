import sqlite3
import os
from flask import Flask, g

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'data.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Create your tables if they don't exist, seed data, etc."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    ''')
    # Seed data if empty
    cursor.execute('SELECT COUNT(*) FROM items')
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO items (name) VALUES ('First item'), ('Second item')")
    conn.commit()

@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)

@app.route('/')
def home():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM items")
    items = cursor.fetchall()
    return f"Items: {items}"

if __name__ == '__main__':
    with app.app_context():
        init_db()  # <-- Run our DB init once, before handling any requests.
    app.run(debug=True, host='0.0.0.0', port=5000)