import jwt
import datetime
import os

# FIXME: Fix environment variable
# Set up the JWT
SECRET_KEY = "1234567890poiuytrewq"#os.getenv('SECRET_KEY')

def login(username, password):

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


