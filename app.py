from flask import Flask, send_from_directory, send_file, request
from linkcheck import analyze_url
from wikiinteractor import analyze_article
from flask_caching import Cache
import os

redis_url = ''

if 'NOTDEV' in os.environ:
    redis_url = 'redis://redis.svc.tools.eqiad1.wikimedia.cloud:6379/0'
else:
    redis_url = 'redis://localhost:6379/2'

config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 1800,
    "CACHE_KEY_PREFIX": "mw-toolforge-link-dispenser",
    "CACHE_REDIS_URL": redis_url
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

@app.route("/api/lookup_url/<url>/<timestamp>")
@cache.cached(timeout=1800)
def lookup_url( url: str, timestamp: str ):
    return analyze_url(url, timestamp)

@app.route("/api/analyze/<path:article_name>")
@cache.cached(timeout=1800, query_string=True)
def analyze( article_name: str ):
    return analyze_article( article_name )

@app.route("/")
def index():
    return send_file('./client/dist/index.html')

@app.route("/<path:filename>")
def serve_other_files( filename: str ):
    print(filename)
    return send_from_directory('./client/dist', filename )

@app.errorhandler(404)
def page_not_found(e):
    print(request.path)
    return send_file('./client/dist/index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1238)