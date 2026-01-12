from flask import Blueprint, request, jsonify, render_template
from services.auth_service import AuthService
from db.firebase_config import verify_firebase_token
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def require_firebase_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        id_token = auth_header.split('Bearer ')[1]
        decoded_token = verify_firebase_token(id_token)
        
        if not decoded_token:
            return jsonify({'error': 'Invalid token'}), 401
        
        request.user_id = decoded_token['uid']
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@auth_bp.route('/profile', methods=['GET'])
def profile_page():
    return render_template('profile.html')

@auth_bp.route('/api/auth/profile', methods=['GET'])
@require_firebase_auth
def get_profile():
    try:
        profile = AuthService.get_user_profile(request.user_id)
        if profile:
            return jsonify(profile), 200
        return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/generate-key', methods=['POST'])
@require_firebase_auth
def generate_key():
    try:
        result = AuthService.generate_api_key(request.user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/api/auth/logout', methods=['POST'])
@require_firebase_auth
def logout():
    try:
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500