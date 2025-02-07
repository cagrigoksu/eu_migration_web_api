from flask import Flask, jsonify, request
from ds import ds_ops
from auth import user_auth
import jwt

# Fetch the dataframe from ds_ops
is_file_exist = ds_ops.check_file_exist()

if(is_file_exist):
    df_eu = ds_ops.get_dataframe()
else:
    ds_ops.prepare_migrations_file() 
    df_eu = ds_ops.get_dataframe()   
    
app = Flask(__name__)

@app.route('/')
def main():
    return 'Europe Immigration/Emigration Analysis'

@app.route('/login', methods=['POST'])
def login():

    username = request.json.get('username')
    password = request.json.get('password')

    token = user_auth.login(username, password)
    
    print(token)
    
    return jsonify({'token': token}), 200
        

@app.route('/migration_data', methods=['GET'])
def get_migration_data():
    
    token = request.headers.get('Authorization')

    if token is None:
        return jsonify({'error': 'Token is missing'}), 401
    
    try:
        print(token)
        # Remove "Bearer " from token
        token = token.split(" ")[1]
        # Decode the token and verify it
        decoded_token = user_auth.decode_token(token)
        print("d_token:", decoded_token)
        #return jsonify({'message': f'Hello, {decoded_token["username"]}! You have access to this protected data.'}), 200
        # Convert the dataframe to JSON format and return it as a response
        if df_eu is not None and not df_eu.empty:
            return jsonify(df_eu.to_dict(orient='records'))
        else:
            return jsonify({"error": "Data not available"}), 500
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401        


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) # Bind to all network interfaces
