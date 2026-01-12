from flask import Blueprint, request
from flasgger import swag_from
from services.analytics_service import analytics_service
from middleware.auth_middleware import require_api_key
from utils.helpers import format_response
from utils.logger import get_logger

logger = get_logger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/trends', methods=['GET'])
@swag_from({
    'tags': ['Analytics'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get migration trend analysis',
    'parameters': [
        {'name': 'country_codes', 'in': 'query', 'type': 'array', 'items': {'type': 'string'}},
        {'name': 'start_year', 'in': 'query', 'type': 'integer'},
        {'name': 'end_year', 'in': 'query', 'type': 'integer'}
    ],
    'responses': {
        200: {'description': 'Trend analysis data'}
    }
})
@require_api_key
def get_trends():
    try:
        countries = request.args.getlist('country_codes')
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)
        
        trends = analytics_service.get_trend_analysis(
            countries if countries else None,
            start_year,
            end_year
        )
        
        if not trends:
            return format_response(error='No data found', status_code=404)
        
        return format_response(data={'trends': trends})
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        return format_response(error='Failed to fetch trends', status_code=500)

@analytics_bp.route('/comparison', methods=['GET'])
@swag_from({
    'tags': ['Analytics'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Compare multiple countries',
    'parameters': [
        {'name': 'country_codes', 'in': 'query', 'type': 'array', 'items': {'type': 'string'}, 'required': True},
        {'name': 'start_year', 'in': 'query', 'type': 'integer'},
        {'name': 'end_year', 'in': 'query', 'type': 'integer'}
    ],
    'responses': {
        200: {'description': 'Country comparison data'},
        400: {'description': 'Missing country codes'}
    }
})
@require_api_key
def get_comparison():
    try:
        countries = request.args.getlist('country_codes')
        
        if not countries:
            return format_response(error='Country codes required', status_code=400)
        
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)
        
        comparison = analytics_service.get_country_comparison(
            countries,
            start_year,
            end_year
        )
        
        if not comparison:
            return format_response(error='No data found', status_code=404)
        
        return format_response(data={'comparison': comparison})
    except Exception as e:
        logger.error(f"Error fetching comparison: {str(e)}")
        return format_response(error='Failed to fetch comparison', status_code=500)

@analytics_bp.route('/top', methods=['GET'])
@swag_from({
    'tags': ['Analytics'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get top countries by metric',
    'parameters': [
        {'name': 'metric', 'in': 'query', 'type': 'string', 'enum': ['immigration', 'emigration', 'net'], 'default': 'net'},
        {'name': 'limit', 'in': 'query', 'type': 'integer', 'default': 10},
        {'name': 'year', 'in': 'query', 'type': 'integer'}
    ],
    'responses': {
        200: {'description': 'Top countries data'}
    }
})
@require_api_key
def get_top_countries():
    try:
        metric = request.args.get('metric', 'net')
        limit = min(request.args.get('limit', 10, type=int), 50)
        year = request.args.get('year', type=int)
        
        top = analytics_service.get_top_countries(metric, limit, year)
        
        return format_response(data={'top_countries': top, 'metric': metric, 'limit': limit})
    except Exception as e:
        logger.error(f"Error fetching top countries: {str(e)}")
        return format_response(error='Failed to fetch top countries', status_code=500)

@analytics_bp.route('/balance', methods=['GET'])
@swag_from({
    'tags': ['Analytics'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get migration balance (positive/negative)',
    'parameters': [
        {'name': 'country_codes', 'in': 'query', 'type': 'array', 'items': {'type': 'string'}},
        {'name': 'start_year', 'in': 'query', 'type': 'integer'},
        {'name': 'end_year', 'in': 'query', 'type': 'integer'}
    ],
    'responses': {
        200: {'description': 'Migration balance data'}
    }
})
@require_api_key
def get_balance():
    try:
        countries = request.args.getlist('country_codes')
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)
        
        balance = analytics_service.get_migration_balance(
            countries if countries else None,
            start_year,
            end_year
        )
        
        if not balance:
            return format_response(error='No data found', status_code=404)
        
        return format_response(data=balance)
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return format_response(error='Failed to fetch balance', status_code=500)

@analytics_bp.route('/growth', methods=['GET'])
@swag_from({
    'tags': ['Analytics'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get year-over-year growth rates',
    'parameters': [
        {'name': 'country_code', 'in': 'query', 'type': 'string'}
    ],
    'responses': {
        200: {'description': 'Growth rate data'}
    }
})
@require_api_key
def get_growth():
    try:
        country = request.args.get('country_code')
        
        growth = analytics_service.get_yearly_growth(country)
        
        return format_response(data={'growth': growth})
    except Exception as e:
        logger.error(f"Error fetching growth: {str(e)}")
        return format_response(error='Failed to fetch growth', status_code=500)

@analytics_bp.route('/correlation', methods=['GET'])
@swag_from({
    'tags': ['Analytics'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get correlation analysis',
    'responses': {
        200: {'description': 'Correlation data'}
    }
})
@require_api_key
def get_correlation():
    try:
        correlation = analytics_service.get_correlation_analysis()
        return format_response(data={'correlation': correlation})
    except Exception as e:
        logger.error(f"Error fetching correlation: {str(e)}")
        return format_response(error='Failed to fetch correlation', status_code=500)

@analytics_bp.route('/distribution', methods=['GET'])
@swag_from({
    'tags': ['Analytics'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get distribution statistics',
    'parameters': [
        {'name': 'metric', 'in': 'query', 'type': 'string', 'enum': ['immigration', 'emigration', 'net'], 'default': 'net'}
    ],
    'responses': {
        200: {'description': 'Distribution statistics'}
    }
})
@require_api_key
def get_distribution():
    try:
        metric = request.args.get('metric', 'net')
        stats = analytics_service.get_distribution_stats(metric)
        return format_response(data={'distribution': stats, 'metric': metric})
    except Exception as e:
        logger.error(f"Error fetching distribution: {str(e)}")
        return format_response(error='Failed to fetch distribution', status_code=500)