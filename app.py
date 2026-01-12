import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_caching import Cache
from flasgger import Swagger
from config import config
from middleware.error_handler import register_error_handlers
from middleware.rate_limiter import setup_rate_limiter
from utils.logger import setup_logger
from utils.helpers import get_version

from routes.auth import auth_bp
from routes.migration import migration_bp
from routes.analytics import analytics_bp
from routes.health import health_bp

def create_app(config_name='default'):
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    setup_logger()
    
    CORS(app)
    cache = Cache(app, config={
        'CACHE_TYPE': app.config['CACHE_TYPE'],
        'CACHE_DEFAULT_TIMEOUT': app.config['CACHE_DEFAULT_TIMEOUT']
    })
    
    limiter = setup_rate_limiter(app)
    
    register_error_handlers(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(migration_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(health_bp)
    
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "EU Migration Web API",
            "description": "API for European migration data analysis",
            "version": get_version(),
            "contact": {
                "name": "API Support",
                "url": "https://github.com/cagrigoksu/eu_migration_web_api"
            }
        },
        "securityDefinitions": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "name": "X-API-KEY",
                "in": "header",
                "description": "API Key Authentication. Get your key by logging in at /login"
            }
        },
        "security": [{"ApiKeyAuth": []}],
        "tags": [
            {"name": "Migration Data", "description": "Migration data endpoints"},
            {"name": "Analytics", "description": "Analytics and aggregation endpoints"},
            {"name": "Health", "description": "Health check endpoints"}
        ]
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    @app.context_processor
    def inject_firebase_config():
        return {
            'firebase_config': {
                'apiKey': app.config['FIREBASE_WEB_API_KEY'],
                'authDomain': app.config['FIREBASE_AUTH_DOMAIN'],
                'projectId': app.config['FIREBASE_PROJECT_ID'],
                'storageBucket': app.config['FIREBASE_STORAGE_BUCKET'],
                'messagingSenderId': app.config['FIREBASE_MESSAGING_SENDER_ID'],
                'appId': app.config['FIREBASE_APP_ID']
            }
        }
    
    @app.route('/')
    def index():
        return render_template('index.html', version=get_version())
    
    @app.route('/integration')
    def integration():
        return render_template('integration.html', version=get_version())
    
    return app


app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )