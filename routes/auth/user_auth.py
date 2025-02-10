from flask import Blueprint, request, jsonify
#import sqlite3
from datetime import datetime, timedelta
import uuid
from pysqlcipher3 import dbapi2 as sqlite
import os

#TODO: change it to environment variable.
ENCRYPTION_KEY = 'secret-key'

auth_bp = Blueprint('auth', __name__)

# Database setup
def init_db():
    db_path = 'apikeys.db'
    first_time_setup = not os.path.exists(db_path)

    conn = sqlite.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA key = '{ENCRYPTION_KEY}';")    
    
    if first_time_setup:
      cursor.execute('''
          CREATE TABLE IF NOT EXISTS api_keys (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              key TEXT UNIQUE NOT NULL,
              issue_date TEXT NOT NULL,
              user_email TEXT UNIQUE NOT NULL
          )
      ''')
      conn.commit()
    conn.close()
    
# create a new API key
def create_api_key(user_email):
    new_key = str(uuid.uuid4())
    issue_date = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite.connect('apikeys.db')
    cursor = conn.cursor()    
    cursor.execute(f"PRAGMA key = '{ENCRYPTION_KEY}';")
    
    cursor.execute('INSERT INTO api_keys (key, issue_date, user_email) VALUES (?, ?, ?)', (new_key, issue_date, user_email))
    conn.commit()
    conn.close()

    return new_key

# validate API key
def is_valid_api_key(api_key):
    conn = sqlite.connect('apikeys.db')
    cursor = conn.cursor()    
    cursor.execute(f"PRAGMA key = '{ENCRYPTION_KEY}';")
    
    cursor.execute("SELECT issue_date FROM api_keys WHERE key = ?", (api_key,))
    result = cursor.fetchone()
    conn.close()

    if result:
        issue_date = datetime.strptime(result[0], '%Y-%m-%d')
        if datetime.now() - issue_date < timedelta(days=30):
            return True
    return False

# handle expired API key
def handle_expired_api_key(api_key):
    conn = sqlite.connect('apikeys.db')
    cursor = conn.cursor()    
    cursor.execute(f"PRAGMA key = '{ENCRYPTION_KEY}';")
    
    cursor.execute("SELECT user_email FROM api_keys WHERE key = ?", (api_key,))
    user = cursor.fetchone()
    cursor.execute("DELETE FROM api_keys WHERE key = ?", (api_key,))
    conn.commit()
    conn.close()

    if user:
        new_api_key = create_api_key(user[0])
        return jsonify({"error": "API key expired. A new API key has been issued.", "new_api_key": new_api_key}), 403
    
    return jsonify({"error": "Invalid API key"}), 403

# decorator to require API key authentication
def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({"error": "API key missing"}), 401
        if not is_valid_api_key(api_key):
            return handle_expired_api_key(api_key)
        return view_function(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['POST'])
def login():
    
    """
    User Login
    ---
    tags:
      - User Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            user_email:
              type: string
              example: user
            password:
              type: string
              example: password
    responses:
      200:
        description: API-Key returned
        schema:
          type: object
          properties:
            api_key:
              type: string
    """

    user_email = request.json.get('user_email')
    password = request.json.get('password')

    if user_email == 'user' and password == 'password':
        api_key = create_api_key(user_email)
        return jsonify({'api_key': api_key, 'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

init_db()

