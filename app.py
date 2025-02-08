from flask import Flask
from flasgger import Swagger


from routes.auth.user_auth import auth_bp 
from routes.data.migration import migration_bp

   
app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(migration_bp, url_prefix='/api/migration_data')

# Swagger Configuration
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Flask JWT API",
        "description": "Simple API with JWT Authentication and Swagger UI",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
        }
    }
})

# # Initialize Swagger
# swagger = Swagger(app)

@app.route('/')
def main():
    return 'Europe Immigration/Emigration Analysis'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) # Bind to all network interfaces
