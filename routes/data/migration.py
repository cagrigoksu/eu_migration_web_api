from flask import Blueprint, request, jsonify
from flasgger import swag_from
from routes.auth.user_auth import is_valid_api_key, handle_expired_api_key, require_api_key
from ds import ds_ops

migration_bp = Blueprint("migration", __name__)

# Initialize the dataframe
if ds_ops.check_file_exist():
    df_eu = ds_ops.get_dataframe()
else:
    ds_ops.prepare_migrations_file()
    df_eu = ds_ops.get_dataframe()

# Utility function to filter dataframe
def filter_data(df, countries=None, start_year=None, end_year=None):
    if countries:
        df = df[df['Country'].isin(countries)]
    if start_year:
        df = df[df['Year'] >= start_year]
    if end_year:
        df = df[df['Year'] <= end_year]
    return df

@migration_bp.route('/migration_data', methods=['GET'], endpoint="get_migration_data")
@swag_from({
    'tags': ['Migration Data - Protected Endpoint'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Retrieve overall migration data.',
    'responses': {
        200: {
            'description': 'Successful access',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'Country': {'type': 'string', 'example': 'Country code'},
                        'Im_Value': {'type': 'number', 'example': 100000},
                        'Em_Value': {'type': 'number', 'example': 100000},
                        'Net_Migration': {'type': 'number', 'example': 100000},
                        'Year': {'type': 'number', 'example': 2011}
                    }
                }
            }
        },
        401: {'description': 'Unauthorized access'}
    }
})
@require_api_key
def get_migration_data():
    if df_eu is not None and not df_eu.empty:
        return jsonify(df_eu.to_dict(orient='records'))
    return jsonify({"error": "Data not available"}), 500

@migration_bp.route('/country', methods=['GET'], endpoint="get_migration_data_by_country")
@swag_from({
    'tags': ['Migration Data - Protected Endpoint'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Retrieve migration data for a list of country codes.',
    'parameters': [
        {
            'name': 'country_codes',
            'in': 'query',
            'required': True,
            'type': 'array',
            'items': {'type': 'string'},
            'collectionFormat': 'multi',
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
@require_api_key
def get_migration_data_by_country():
    country_codes = request.args.getlist('country_codes')
    if not country_codes:
        return jsonify({'error': 'No country codes provided'}), 400

    filtered_df = filter_data(df_eu, countries=country_codes)
    return jsonify(filtered_df.to_dict(orient='records')) if not filtered_df.empty else jsonify({"error": "Data not available"}), 500

@migration_bp.route('/year', methods=['GET'], endpoint="get_migration_data_by_year")
@swag_from({
    'tags': ['Migration Data - Protected Endpoint'],
    'security': [{'ApiKeyAuth': []}],
    'description': 'Retrieve migration data for a specific year or a range of years.',
    'parameters': [
        {'name': 'start_year', 'in': 'query', 'type': 'integer', 'description': 'Start year'},
        {'name': 'end_year', 'in': 'query', 'type': 'integer', 'description': 'End year'},
        {'name': 'year', 'in': 'query', 'type': 'integer', 'description': 'Specific year (overrides start/end year if provided)'}
    ],
    'responses': {
        200: {
            'description': 'Successful response with migration data.',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'Country': {'type': 'string', 'example': 'USA'},
                        'Im_Value': {'type': 'number', 'example': 120000},
                        'Em_Value': {'type': 'number', 'example': 90000},
                        'Net_Migration': {'type': 'number', 'example': 30000},
                        'Year': {'type': 'number', 'example': 2015}
                    }
                }
            }
        },
        400: {'description': 'Invalid request. Provide at least one year parameter.'}
    }
})
@require_api_key
def get_migration_data_by_year():
    year = request.args.get('year', type=int)
    start_year = request.args.get('start_year', type=int)
    end_year = request.args.get('end_year', type=int)

    if not any([year, start_year, end_year]):
        return jsonify({'error': 'Provide at least one year parameter'}), 400

    if year:
        start_year = end_year = year

    filtered_df = filter_data(df_eu, start_year=start_year, end_year=end_year)
    return jsonify(filtered_df.to_dict(orient='records')) if not filtered_df.empty else jsonify({"error": "Data not available"}), 500

