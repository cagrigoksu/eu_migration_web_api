from flask import Blueprint
from flasgger import swag_from
from services.data_service import data_service
from db.database import db
from utils.helpers import format_response, get_version
from utils.logger import get_logger

logger = get_logger(__name__)

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
@swag_from({
    'tags': ['Health'],
    'description': 'Health check endpoint',
    'responses': {
        200: {
            'description': 'Service is healthy',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'version': {'type': 'string'},
                    'database': {'type': 'boolean'},
                    'dataset': {'type': 'boolean'}
                }
            }
        }
    }
})
def health_check():
    """Health check endpoint"""
    try:
        # check db
        db_healthy = False
        try:
            with db.get_connection():
                db_healthy = True
        except Exception:
            pass
        
        # check dataset
        dataset_healthy = False
        try:
            df = data_service.get_all_data()
            dataset_healthy = df is not None and not df.empty
        except Exception:
            pass
        
        status = 'healthy' if (db_healthy and dataset_healthy) else 'degraded'
        
        return format_response(data={
            'status': status,
            'version': get_version(),
            'database': db_healthy,
            'dataset': dataset_healthy
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return format_response(
            data={'status': 'unhealthy'},
            error=str(e),
            status_code=500
        )

@health_bp.route('/ping', methods=['GET'])
def ping():
    return format_response(data={'message': 'pong'})
