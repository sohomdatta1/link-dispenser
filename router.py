from flask import Flask, send_from_directory, send_file, request, make_response
from linkcheck import analyze_url
from wikiinteractor import analyze_article_and_urls
from app import flask_app as app, cache
from jobs import push_analysis, fetch_analysis
from redis_init import rediscl as rcl
from re import compile as re_compile

WIKIMEDIA_ORIGIN_PATTERN = re_compile(
    r"^https:\/\/([a-z\-]+\.)?(wikipedia|wikimedia|wiktionary|wikibooks|wikinews|wikiquote|wikisource|wikiversity|wikivoyage|wikidata|mediawiki|wikimediafoundation)\.org$"
)

@app.route("/api/lookup_url/<url>")
@cache.cached(timeout=1800, query_string=True)
def lookup_url(url: str):
    return analyze_url(url)

@app.route("/api/healthz")
def healthz():
    try:
        rcl.ping()
    except Exception as _:
        return 500, 'BORKEN!'
    return 'OK'

@app.route("/api/citeunseen/<path:url>")
@cache.cached(timeout=1800, query_string=True)
def citeunseen(url: str):
    from citeuseen import annotate_url as annotate_url_with_citeunseen_data
    return annotate_url_with_citeunseen_data(url)


@app.route("/api/analyze/<path:article_name>")
@cache.cached(timeout=1800, query_string=True)
def analyze(article_name: str):
    return analyze_article_and_urls(article_name)


@cache.memoize(timeout=82800)
def cached_push_analysis(article_name: str, _query_params: dict = None):
    return push_analysis(article_name)

@app.route("/api/push_analysis/<path:article_name>")
def push_analysis_handler(article_name: str):
    article_name = article_name.replace('+', ' ')
    query_params = request.args.to_dict()

    cache_key = cached_push_analysis.make_cache_key(
        cached_push_analysis.uncached,
        *[article_name, query_params]
    )

    cached_hit = cache.get(cache_key) is not None

    result = cached_push_analysis(article_name, query_params)
    result['cached'] = cached_hit

    return make_response(result)

@app.after_request
def add_acao_header(response):
    origin = request.headers.get("Origin")
    if origin and WIKIMEDIA_ORIGIN_PATTERN.match(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    return response

@app.route("/api/fetch_analysis/<uuid>")
def fetch_analysis_handler(uuid: str):
    return fetch_analysis(uuid)

@app.route("/")
def index():
    r = send_file('./client/dist/index.html')
    r.headers['Cache-Control'] = 'max-age=604800'
    return r

@app.route("/robots.txt")

def robots_txt():
    content = open('robots.txt', encoding='utf-8').read()
    response = make_response(content)
    response.headers["Content-Type"] = "text/plain, charset=utf-8"
    return response

@app.route("/<path:filename>")
def serve_other_files(filename: str):
    r = send_from_directory('./client/dist', filename)
    r.headers['Cache-Control'] = 'max-age=604800'
    return r


@app.errorhandler(404)
def page_not_found(_):
    r = send_file('./client/dist/index.html')
    r.headers['Cache-Control'] = 'max-age=604800'
    return r


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1238)
