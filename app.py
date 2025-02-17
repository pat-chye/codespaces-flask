import os
import sqlite3

from flask import Flask, g, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "CHANGE_ME_TO_SOMETHING_SECURE"  # Needed for sessions

DATABASE = os.path.join(os.path.dirname(__file__), 'data.db')

# ---------------------------------------------------
# 1) Database helpers
# ---------------------------------------------------
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
    """Create 'users' table if it doesn't exist."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    conn.commit()

# Initialize DB at startup
with app.app_context():
    init_db()

# ---------------------------------------------------
# 2) Routes
# ---------------------------------------------------
@app.route('/service-worker.js')
def sw():
    """Serve service-worker.js for PWA."""
    response = send_from_directory('static', 'service-worker.js')
    response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/')
def root():
    """Redirect to login page by default (or could show a landing page)."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page. GET -> show form, POST -> check credentials."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, password FROM users WHERE email=?", (email,))
        row = cursor.fetchone()

        if row:
            user_id, first_name, hashed_pw = row
            # Check the hashed password
            if check_password_hash(hashed_pw, password):
                # Correct password: store session, go to welcome
                session['user_id'] = user_id
                session['first_name'] = first_name
                return redirect(url_for('welcome'))
            else:
                return render_template('login.html', error="Invalid password.")
        else:
            return render_template('login.html', error="No account found with that email.")

    # If GET, just show the login form
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page. GET -> form, POST -> create user and redirect to welcome."""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name  = request.form.get('last_name')
        email      = request.form.get('email')
        password   = request.form.get('password')

        # Hash the password before storing
        hashed_pw = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (first_name, last_name, email, password)
                VALUES (?, ?, ?, ?)
            ''', (first_name, last_name, email, hashed_pw))
            conn.commit()
        except sqlite3.IntegrityError:
            # Likely a duplicate email
            return render_template('signup.html', error="Email already registered. Please log in.")

        # Store session, greet user
        cursor.execute("SELECT id FROM users WHERE email=?", (email,))
        user_row = cursor.fetchone()
        if user_row:
            session['user_id'] = user_row[0]
            session['first_name'] = first_name
            return redirect(url_for('welcome'))

        # Fallback error
        return render_template('signup.html', error="Signup failed unexpectedly.")

    # If GET, show signup form
    return render_template('signup.html')

@app.route('/welcome')
def welcome():
    """Show a simple welcome page if logged in, else redirect to login."""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # We stored first_name in session at login/signup
    first_name = session.get('first_name', 'User')
    return render_template('welcome.html', first_name=first_name)

@app.route('/logout')
def logout():
    """Clear the session and go back to login."""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Run the Flask dev server
    app.run(debug=True, host='0.0.0.0', port=5000)