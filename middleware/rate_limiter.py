from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
from config import Config

def get_api_key():
    #* extract apikey from request for rate limiting
    return request.headers.get('X-API-KEY', get_remote_address())

def setup_rate_limiter(app):
    #* rate limiter 
    limiter = Limiter(
        app=app,
        key_func=get_api_key,
        default_limits=[
            f"{Config.RATE_LIMIT_PER_HOUR} per hour",
            f"{Config.RATE_LIMIT_PER_DAY} per day"
        ],
        storage_uri="memory://",
        strategy="fixed-window"
    )
    
    return limiter
