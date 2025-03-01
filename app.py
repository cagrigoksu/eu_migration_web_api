from flask import Flask, render_template
from flasgger import Swagger

from routes.auth.user_auth import auth_bp 
from routes.data.migration import migration_bp
from routes.analytics.analytics import analytics_bp, create_dash_app
   
app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(migration_bp, url_prefix='/api/migration')
app.register_blueprint(analytics_bp, url_prefix='/analytics')
create_dash_app(app)

def get_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "unknown"

# Swagger Configuration
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Flask API",
        "description": "Simple API with ApiKeyAuth Authentication and Swagger UI",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "name": "X-API-KEY",
            "in": "header",
            "description": "API Key Authentication. Provide the key in the 'X-API-KEY' header."
        }
    },
    "security": [
        {
            "ApiKeyAuth": []
        }
        ]
})

# # Initialize Swagger
# swagger = Swagger(app)

@app.route('/')
def main():
    version = get_version()
    #return f'Europe Immigration/Emigration Analysis on AWS EC2 - Version: {version}'
    return render_template("index.html", version=version)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 
