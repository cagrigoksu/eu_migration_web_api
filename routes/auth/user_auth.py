from flask import Blueprint, request, jsonify
import jwt
import datetime
import os

auth_bp = Blueprint('auth', __name__)

# FIXME: Fix environment variable
# Set up the JWT
SECRET_KEY = "1234567890poiuytrewq"#os.getenv('SECRET_KEY')

def user_login(username, password):

    if username == 'user' and password == 'password':
        
        # Create a JWT token 
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.now() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')

        return token
    else:
        return None
    
def decode_token(token):
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    return decoded_token

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
            username:
              type: string
              example: user
            password:
              type: string
              example: password
    responses:
      200:
        description: JWT Token returned
        schema:
          type: object
          properties:
            token:
              type: string
    """

    username = request.json.get('username')
    password = request.json.get('password')

    token = user_login(username, password)
    
    print(token)
    
    return jsonify({'token': token}), 200

