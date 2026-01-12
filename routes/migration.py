from flask import Blueprint, request
from flasgger import swag_from
from services.data_service import data_service
from middleware.auth_middleware import require_api_key
from utils.helpers import paginate_data, format_response
from utils.logger import get_logger

logger = get_logger(__name__)

migration_bp = Blueprint('migration', __name__, url_prefix='/api/migration')

@migration_bp.route('/data', methods=['GET'])
@swag_from({
    'tags': ['Migration Data'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Retrieve migration data with optional filtering and pagination',
    'parameters': [
        {'name': 'country_codes', 'in': 'query', 'type': 'array', 'items': {'type': 'string'}, 
         'description': 'Filter by country codes (comma-separated)'},
        {'name': 'start_year', 'in': 'query', 'type': 'integer', 'description': 'Start year'},
        {'name': 'end_year', 'in': 'query', 'type': 'integer', 'description': 'End year'},
        {'name': 'year', 'in': 'query', 'type': 'integer', 'description': 'Specific year'},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'default': 1, 'description': 'Page number'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'default': 100, 'description': 'Items per page'}
    ],
    'responses': {
        200: {'description': 'Successful response with migration data'},
        401: {'description': 'Unauthorized'}
    }
})
@require_api_key
def get_migration_data():
    try:
        country_codes = request.args.getlist('country_codes')
        start_year = request.args.get('start_year', type=int)
        end_year = request.args.get('end_year', type=int)
        year = request.args.get('year', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 100, type=int), 1000)
        
        filtered_df = data_service.filter_data(
            countries=country_codes if country_codes else None,
            start_year=start_year,
            end_year=end_year,
            year=year
        )
        
        if filtered_df.empty:
            return format_response(
                data={'items': [], 'pagination': {'page': 1, 'per_page': per_page, 'total': 0, 'pages': 0}},
                message='No data found for the given filters'
            )
        
        result = paginate_data(filtered_df, page, per_page)
        
        return format_response(data=result)
        
    except Exception as e:
        logger.error(f"Error fetching migration data: {str(e)}")
        return format_response(error='Failed to fetch data', status_code=500)

@migration_bp.route('/countries', methods=['GET'])
@swag_from({
    'tags': ['Migration Data'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get list of available countries',
    'responses': {
        200: {
            'description': 'List of country codes',
            'schema': {
                'type': 'object',
                'properties': {
                    'countries': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        }
    }
})
@require_api_key
def get_countries():
    try:
        countries = data_service.get_available_countries()
        return format_response(data={'countries': countries, 'count': len(countries)})
    except Exception as e:
        logger.error(f"Error fetching countries: {str(e)}")
        return format_response(error='Failed to fetch countries', status_code=500)

@migration_bp.route('/years', methods=['GET'])
@swag_from({
    'tags': ['Migration Data'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get list of available years',
    'responses': {
        200: {
            'description': 'List of years',
            'schema': {
                'type': 'object',
                'properties': {
                    'years': {'type': 'array', 'items': {'type': 'integer'}}
                }
            }
        }
    }
})
@require_api_key
def get_years():
    try:
        years = data_service.get_available_years()
        return format_response(data={'years': years, 'count': len(years)})
    except Exception as e:
        logger.error(f"Error fetching years: {str(e)}")
        return format_response(error='Failed to fetch years', status_code=500)

@migration_bp.route('/country/<country_code>', methods=['GET'])
@swag_from({
    'tags': ['Migration Data'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get summary for a specific country',
    'parameters': [
        {'name': 'country_code', 'in': 'path', 'type': 'string', 'required': True}
    ],
    'responses': {
        200: {'description': 'Country summary'},
        404: {'description': 'Country not found'}
    }
})
@require_api_key
def get_country_summary(country_code):
    try:
        summary = data_service.get_country_summary(country_code.upper())
        
        if not summary:
            return format_response(error='Country not found', status_code=404)
        
        return format_response(data=summary)
    except Exception as e:
        logger.error(f"Error fetching country summary: {str(e)}")
        return format_response(error='Failed to fetch country summary', status_code=500)

@migration_bp.route('/year/<int:year>', methods=['GET'])
@swag_from({
    'tags': ['Migration Data'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get summary for a specific year',
    'parameters': [
        {'name': 'year', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Year summary'},
        404: {'description': 'Year not found'}
    }
})
@require_api_key
def get_year_summary(year):
    try:
        summary = data_service.get_year_summary(year)
        
        if not summary:
            return format_response(error='Year not found', status_code=404)
        
        return format_response(data=summary)
    except Exception as e:
        logger.error(f"Error fetching year summary: {str(e)}")
        return format_response(error='Failed to fetch year summary', status_code=500)

@migration_bp.route('/statistics', methods=['GET'])
@swag_from({
    'tags': ['Migration Data'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Get overall statistics',
    'responses': {
        200: {'description': 'Overall statistics'}
    }
})
@require_api_key
def get_statistics():
    try:
        stats = data_service.get_statistics()
        return format_response(data=stats)
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        return format_response(error='Failed to fetch statistics', status_code=500)