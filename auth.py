import os
from functools import wraps
from typing import Optional

from authlib.integrations.flask_client import OAuth
from flask import Response, jsonify, redirect, request, session, url_for

OAUTH_AUTHORIZE_URL = os.getenv(
    "WIKIMEDIA_OAUTH_AUTHORIZE_URL",
    "https://meta.wikimedia.org/w/rest.php/oauth2/authorize",
)
OAUTH_TOKEN_URL = os.getenv(
    "WIKIMEDIA_OAUTH_TOKEN_URL",
    "https://meta.wikimedia.org/w/rest.php/oauth2/access_token",
)
OAUTH_PROFILE_URL = os.getenv(
    "WIKIMEDIA_OAUTH_PROFILE_URL",
    "https://meta.wikimedia.org/w/rest.php/oauth2/resource/profile",
)
OAUTH_CLIENT_ID = os.getenv("WIKIMEDIA_OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("WIKIMEDIA_OAUTH_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.getenv("WIKIMEDIA_OAUTH_REDIRECT_URI")
OAUTH_SCOPE = os.getenv("WIKIMEDIA_OAUTH_SCOPE", "basic")


def init_oauth(app):
    oauth = OAuth(app)
    oauth.register(
        name="wikimedia",
        client_id=OAUTH_CLIENT_ID,
        client_secret=OAUTH_CLIENT_SECRET,
        authorize_url=OAUTH_AUTHORIZE_URL,
        access_token_url=OAUTH_TOKEN_URL,
        client_kwargs={
            "scope": OAUTH_SCOPE,
            "token_endpoint_auth_method": "client_secret_post",
        },
    )
    return oauth


def _is_api_request() -> bool:
    return request.path.startswith("/api/")


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            if _is_api_request():
                return jsonify({"error": "auth_required"}), 401
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def _fetch_profile(oauth_client) -> Optional[dict]:
    if "token" not in session:
        return None
    response = oauth_client.get(OAUTH_PROFILE_URL, token=session["token"])
    if response.status_code != 200:
        return None
    return response.json()


def register_auth_routes(app):
    oauth = init_oauth(app)

    @app.route("/login")
    def login():
        if not OAUTH_CLIENT_ID or not OAUTH_CLIENT_SECRET:
            return Response("OAuth client not configured", status=500)
        if "next" in request.args:
            session["next"] = request.args.get("next")
        redirect_uri = OAUTH_REDIRECT_URI or url_for("auth_callback", _external=True)
        return oauth.wikimedia.authorize_redirect(redirect_uri)

    @app.route("/auth/callback")
    def auth_callback():
        token = oauth.wikimedia.authorize_access_token()
        session["token"] = token
        profile = _fetch_profile(oauth.wikimedia)
        if profile:
            session["user"] = profile
        else:
            session.pop("token", None)
            return Response("OAuth profile lookup failed", status=401)
        next_url = session.pop("next", None)
        return redirect(next_url or "/")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")

    @app.route("/api/whoami")
    def whoami():
        user = session.get("user")
        if not user:
            return jsonify({"authenticated": False}), 200
        return jsonify({"authenticated": True, "user": user}), 200
