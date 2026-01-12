from flask import jsonify

def paginate_data(data, page=1, per_page=100):
    if hasattr(data, 'iloc'):
        total = len(data)
        start = (page - 1) * per_page
        end = start + per_page
        items = data.iloc[start:end].to_dict(orient='records')
    else:
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