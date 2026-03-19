from flask import Flask
from celery_init import celery_init_app
from redis_init import redis_url, REDIS_KEY_PREFIX, rediscl
from flask_caching import Cache
from flask_session import Session
import os

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url=redis_url,
            result_backend=redis_url,
            retry_policy={
                'max_retries': 10 * 1000, # absurdly high
                'interval_start': 2,
                'interval_step': 2
            },
            task_default_queue=REDIS_KEY_PREFIX + '-celery-queue',
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
    app.config.setdefault('SESSION_TYPE', 'redis')
    app.config.setdefault('SESSION_REDIS', rediscl)
    app.config.setdefault('SESSION_PERMANENT', False)
    app.config.setdefault('SESSION_USE_SIGNER', True)
    app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
    app.config.setdefault('SESSION_COOKIE_SECURE', 'NOTDEV' in os.environ)
    celery_init_app(app)
    Session(app)
    return app

flask_app = create_app()
config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 1800,
    "CACHE_KEY_PREFIX": REDIS_KEY_PREFIX,
    "CACHE_REDIS_URL": redis_url
}

flask_app.config.from_mapping(config)
cache = Cache(flask_app)
celery = flask_app.extensions['celery']