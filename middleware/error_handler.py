from flask import jsonify
from marshmallow import ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

class APIError(Exception):
    
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv

def register_error_handlers(app):
    
    #* register error handlers for the app    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        logger.error(f"API Error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger.error(f"Validation Error: {error.messages}")
        return jsonify({
            'error': 'Validation failed',
            'details': error.messages
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested resource does not exist'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"Internal Server Error: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.error(f"Unexpected Error: {str(error)}", exc_info=True)
        return jsonify({
            'error': 'Unexpected error',
            'message': str(error) if app.debug else 'An unexpected error occurred'
        }), 500
