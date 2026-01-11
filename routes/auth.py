from flask import Blueprint, request, jsonify
from flasgger import swag_from
from marshmallow import ValidationError
from db.database import db
from config import Config
from utils.validators import LoginSchema
from utils.helpers import format_response
from utils.logger import get_logger

#TODO add logic to register new user and api key 
#? maybe use firebase, firestore auth

logger = get_logger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'description': 'Login to get API key',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'user_email': {'type': 'string', 'example': 'user@example.com'},
                'password': {'type': 'string', 'example': 'password123'}
            },
            'required': ['user_email', 'password']
        }
    }],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'api_key': {'type': 'string'},
                    'message': {'type': 'string'},
                    'expiry_days': {'type': 'integer'}
                }
            }
        },
        400: {'description': 'Validation error'},
        401: {'description': 'Invalid credentials'}
    }
})
def login():
    #! login endpoint to get API key
    try:
        schema = LoginSchema()
        data = schema.load(request.get_json())
        
        user_email = data['user_email']
        password = data['password']
        
        if user_email == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            existing_key = db.get_user_key(user_email)
            
            if existing_key and db.is_valid_api_key(existing_key):
                logger.info(f"User {user_email} retrieved existing API key")
                return format_response(
                    data={
                        'api_key': existing_key,
                        'message': 'Using existing API key',
                        'expiry_days': Config.API_KEY_EXPIRY_DAYS
                    }
                )
            
            # create new key
            api_key = db.create_api_key(user_email)
            logger.info(f"New API key created for {user_email}")
            
            return format_response(
                data={
                    'api_key': api_key,
                    'message': 'Login successful',
                    'expiry_days': Config.API_KEY_EXPIRY_DAYS
                }
            )
        else:
            logger.warning(f"Failed login attempt for {user_email}")
            return format_response(
                error='Invalid credentials',
                status_code=401
            )
            
    except ValidationError as e:
        return format_response(
            error='Validation failed',
            data={'details': e.messages},
            status_code=400
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return format_response(
            error='Login failed',
            status_code=500
        )

@auth_bp.route('/verify', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Verify API key validity',
    'responses': {
        200: {
            'description': 'API key is valid',
            'schema': {
                'type': 'object',
                'properties': {
                    'valid': {'type': 'boolean'},
                    'message': {'type': 'string'}
                }
            }
        },
        401: {'description': 'Invalid API key'}
    }
})
def verify():
    #! verify API key
    api_key = request.headers.get('X-API-KEY')
    
    if not api_key:
        return format_response(
            data={'valid': False},
            error='API key missing',
            status_code=401
        )
    
    is_valid = db.is_valid_api_key(api_key)
    
    if is_valid:
        return format_response(
            data={'valid': True, 'message': 'API key is valid'}
        )
    else:
        return format_response(
            data={'valid': False},
            error='Invalid or expired API key',
            status_code=401
        )
