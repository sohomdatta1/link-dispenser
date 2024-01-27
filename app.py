from flask import Flask
from celery_init import celery_init_app
from redis_init import redis_url, REDIS_KEY_PREFIX
from flask_caching import Cache

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        CELERY=dict(
            broker_url=redis_url,
            result_backend=redis_url,
            task_default_queue=REDIS_KEY_PREFIX + '-celery-queue',
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)
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