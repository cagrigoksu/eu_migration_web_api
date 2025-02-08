from flask import Blueprint, request, jsonify
from flasgger import swag_from
from routes.auth import user_auth
from ds import ds_ops
import jwt

migration_bp = Blueprint("migration", __name__)

# Fetch the dataframe from ds_ops
is_file_exist = ds_ops.check_file_exist()

if(is_file_exist):
    df_eu = ds_ops.get_dataframe()
else:
    ds_ops.prepare_migrations_file() 
    df_eu = ds_ops.get_dataframe()   

        
# TODO: Control country and year filters
@migration_bp.route('/migration_data', methods=['GET'])
def get_migration_data():
    
    """
    Migration_data
    ---
    tags:
      - Migration Data - Protected Endpoint
    security:
      - Bearer: []
    responses:
      200:
        description: Successful access
        schema:
          type: object
          properties:
            Country:
              type: string
              example: Country code
            Im_Value:
              type: number
              example: 100000
            Em_Value:
                type: number
                example: 100000
            Net_Migration:
                type: number
                example: 100000
            Year:
                type: number
                example: 2011

      401:
        description: Unauthorized access
    """
    
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
    
    
@migration_bp.route('/country' , methods=['GET'])
@swag_from({
    'tags': ['Migration Data - Protected Endpoint'],
    'security': [{'Bearer': []}],
    'description': 'Retrieve migration data for a list of country codes.',
    'parameters': [
        {
            'name': 'country_codes',
            'in': 'query',         # Use query instead of body
            'required': True,
            'type': 'array',
            'items': {'type': 'string'},
            'collectionFormat': 'multi',  # Allows multiple query params like ?country_codes=USA&country_codes=CAN
            'description': 'List of country codes'
        }
    ],
    'responses': {
        200: {
            'description': 'Successful response with migration data.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'Country': {'type': 'string', 'example': 'AUT'},
                        'Im_Value': {'type': 'number', 'example': 100000},
                        'Em_Value': {'type': 'number', 'example': 80000},
                        'Net_Migration': {'type': 'number', 'example': 20000},
                        'Year': {'type': 'number', 'example': 2021}
                    }
                }
            }
        },
        400: {'description': 'Invalid request. Missing or incorrect country_codes.'}
    }
})
def get_migration_data_by_country():
  
    country_codes = request.args.getlist('country_codes')
    print(country_codes)
    
    token = request.headers.get('Authorization')

    if token is None:
        return jsonify({'error': 'Token is missing'}), 401
    
    try:    
      if df_eu is not None and not df_eu.empty:
        filtered_df = df_eu[df_eu['Country'].isin(country_codes)]
        return jsonify(filtered_df.to_dict(orient='records'))
      else:
        return jsonify({"error": "Data not available"}), 500
    except jwt.ExpiredSignatureError:
      return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
      return jsonify({'error': 'Invalid token'}), 401    