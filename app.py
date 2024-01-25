from flask import Flask, send_from_directory, send_file, request
from linkcheck import analyze_url
from wikiinteractor import analyze_article_and_urls
from flask_caching import Cache
from jobs import push_analysis, fetch_analysis
from redis_init import redis_url, REDIS_KEY_PREFIX

config = {
    "DEBUG": True,
    "CACHE_TYPE": "RedisCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 1800,
    "CACHE_KEY_PREFIX": REDIS_KEY_PREFIX,
    "CACHE_REDIS_URL": redis_url
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


@app.route("/api/lookup_url/<url>/<timestamp>")
@cache.cached(timeout=1800, query_string=True)
def lookup_url(url: str):
    return analyze_url(url)


@app.route("/api/analyze/<path:article_name>")
@cache.cached(timeout=1800, query_string=True)
def analyze(article_name: str):
    return analyze_article_and_urls(article_name)


@app.route("/api/push_analysis/<path:article_name>")
@cache.cached(timeout=82800, query_string=True)
def push_analysis_handler(article_name: str):
    return push_analysis(article_name)


@app.route("/api/fetch_analysis/<uuid>")
def fetch_analysis_handler(uuid: str):
    return fetch_analysis(uuid)


@app.route("/")
def index():
    r = send_file('./client/dist/index.html')
    r.headers['Cache-Control'] = 'max-age=604800'
    return r


@app.route("/<path:filename>")
def serve_other_files(filename: str):
    r = send_from_directory('./client/dist', filename)
    r.headers['Cache-Control'] = 'max-age=604800'
    return r


@app.errorhandler(404)
def page_not_found(e):
    r = send_file('./client/dist/index.html')
    r.headers['Cache-Control'] = 'max-age=604800'
    return r


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1238)
