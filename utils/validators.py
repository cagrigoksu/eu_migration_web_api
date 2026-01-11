import re
from marshmallow import Schema, fields, validate, ValidationError

class EmailValidator:
    
    @staticmethod
    def is_valid(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

class YearValidator:
    
    @staticmethod
    def is_valid(year):
        try:
            year = int(year)
            return 1900 <= year <= 2100
        except (ValueError, TypeError):
            return False

class CountryCodeValidator:
    
    VALID_CODES = {
        'AUT', 'BEL', 'BGR', 'CHE', 'CYP', 'CZE', 'DEU', 'DNK', 'EST', 'GRC',
        'ESP', 'FIN', 'FRA', 'GEO', 'HRV', 'HUN', 'IRL', 'ISL', 'ITA', 'LIE',
        'LTU', 'LUX', 'LVA', 'MDA', 'MNE', 'MKD', 'MLT', 'NLD', 'NOR', 'POL',
        'PRT', 'ROU', 'SWE', 'SVN', 'SVK', 'TUR', 'GBR'
    }
    
    @staticmethod
    def is_valid(code):
        return code.upper() in CountryCodeValidator.VALID_CODES
    
    @staticmethod
    def validate_list(codes):
        if not codes:
            return False
        return all(CountryCodeValidator.is_valid(code) for code in codes)

class LoginSchema(Schema):
    user_email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class MigrationQuerySchema(Schema):
    country_codes = fields.List(fields.Str(), missing=None)
    start_year = fields.Int(validate=validate.Range(min=1900, max=2100), missing=None)
    end_year = fields.Int(validate=validate.Range(min=1900, max=2100), missing=None)
    year = fields.Int(validate=validate.Range(min=1900, max=2100), missing=None)
    page = fields.Int(validate=validate.Range(min=1), missing=1)
    per_page = fields.Int(validate=validate.Range(min=1, max=1000), missing=100)

class AnalyticsQuerySchema(Schema):
    countries = fields.List(fields.Str(), missing=None)
    start_year = fields.Int(validate=validate.Range(min=1900, max=2100), missing=None)
    end_year = fields.Int(validate=validate.Range(min=1900, max=2100), missing=None)
    metric = fields.Str(validate=validate.OneOf(['immigration', 'emigration', 'net']), missing='net')
