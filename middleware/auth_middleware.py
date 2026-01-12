from functools import wraps
from flask import request, jsonify
from services.auth_service import AuthService

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        
        if not api_key:
            return jsonify({'error': 'API key missing'}), 401
        
        if not AuthService.validate_api_key(api_key):
            return jsonify({'error': 'Invalid or expired API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function