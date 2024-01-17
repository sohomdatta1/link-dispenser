from flask import Flask, send_from_directory, send_file
from linkcheck import analyze_url
from wikiinteractor import analyze_article

app = Flask(__name__)

@app.route("/api/lookup_url/<url>/<timestamp>")
def lookup_url( url: str, timestamp: str ):
    return analyze_url(url, timestamp)

@app.route("/api/analyze/<article_name>")
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
    return send_file('./client/dist/index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1238)