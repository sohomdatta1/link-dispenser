import datetime
import os, json, time, base64, hashlib
from flask import Flask, Response, request
from requests import Request
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from http_message_signatures import HTTPMessageSigner, HTTPSignatureKeyResolver, algorithms

def load_jwk():
    jwks_path = os.getenv("BOT_AUTH_JWKS_FILE")
    if not jwks_path:
        raise RuntimeError("BOT_AUTH_JWKS_FILE not set")
    with open(jwks_path, "r") as f:
        return json.load(f)

def jwk_thumbprint(jwk: dict) -> str:
    data = {"crv": jwk["crv"], "kty": jwk["kty"], "x": jwk["x"]}
    digest = hashlib.sha256(
        json.dumps(data, separators=(",", ":"), sort_keys=True).encode()
    ).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()

def _base64url_decode(val): return base64.urlsafe_b64decode(val + "=" * (-len(val) % 4))

class SingleKeyResolver(HTTPSignatureKeyResolver):
    def __init__(self, key): self.key = key
    def resolve_private_key(self, key_id: str): return self.key
    def resolve_public_key(self, key_id: str): return self.key.public_key()

def init_bot_auth_middleware(app: Flask):
    jwk = load_jwk()
    priv = Ed25519PrivateKey.from_private_bytes(_base64url_decode(jwk["d"]))
    key_id = jwk_thumbprint(jwk)

    @app.route("/.well-known/http-message-signatures-directory")
    def directory():
        body = json.dumps({
            "keys": [{
                "kty": "OKP",
                "crv": jwk["crv"],
                "x": jwk["x"]
            }]
        })
        created = datetime.datetime.now(datetime.timezone.utc)
        expires = created + datetime.timedelta(minutes=5)

        resolver = SingleKeyResolver(priv)
        signer = HTTPMessageSigner(signature_algorithm=algorithms.ED25519, key_resolver=resolver)
        fake_req = Request("GET", f"https://{request.host}/.well-known/http-message-signatures-directory")
        fake_req.headers["Content-Type"] = "application/http-message-signatures-directory+json"
        for k, v in request.headers.items():
            fake_req.headers[k] = v

        signer.sign(
            fake_req,
            key_id=key_id,
            covered_component_ids=("@authority",),
            created=created,
            expires=expires,
            tag="http-message-signatures-directory"
        )

        resp = Response(body, mimetype="application/http-message-signatures-directory+json")
        resp.headers["Signature"] = fake_req.headers["Signature"]
        resp.headers["Signature-Input"] = fake_req.headers["Signature-Input"]
        resp.headers["Cache-Control"] = "max-age=86400"
        return resp