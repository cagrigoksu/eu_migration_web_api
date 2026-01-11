from functools import wraps
from flask import request, jsonify
from db.database import db
from utils.logger import get_logger

logger = get_logger(__name__)

def require_api_key(f):
    #! decorator to require api key auth
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        
        if not api_key:
            logger.warning("API request without key")
            return jsonify({"error": "API key missing"}), 401
        
        if not db.is_valid_api_key(api_key):
            logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
            return jsonify({"error": "Invalid or expired API key"}), 401

        db.log_api_usage(api_key, request.path, 200)
        
        return f(*args, **kwargs)
    
    return decorated_function

def paginate_data(data, page=1, per_page=100):
    if hasattr(data, 'iloc'):  # df
        total = len(data)
        start = (page - 1) * per_page
        end = start + per_page
        items = data.iloc[start:end].to_dict(orient='records')
    else:  # list
        total = len(data)
        start = (page - 1) * per_page
        end = start + per_page
        items = data[start:end]
    
    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }

def format_response(data=None, message=None, error=None, status_code=200):
    response = {}
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    if error:
        response['error'] = error
    
    return jsonify(response), status_code

def get_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "1.0.0"
