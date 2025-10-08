# bot_auth_requests.py
import os, json, base64, time
from datetime import datetime, timedelta, timezone
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from http_message_signatures import HTTPMessageSigner, HTTPSignatureKeyResolver, algorithms
from requests.adapters import HTTPAdapter
import requests

def _base64url_decode(val): return base64.urlsafe_b64decode(val + "=" * (-len(val) % 4))

class SingleKeyResolver(HTTPSignatureKeyResolver):
    def __init__(self, key): self.key = key
    def resolve_private_key(self, key_id): return self.key
    def resolve_public_key(self, key_id): return self.key.public_key()

class WebBotAuthAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        jwks_path = os.getenv("BOT_AUTH_JWKS_FILE")
        if not jwks_path:
            raise RuntimeError("BOT_AUTH_JWKS_FILE not set")
        with open(jwks_path, "r", encoding='utf-8') as f:
            jwk = json.load(f)
        self.private_key = Ed25519PrivateKey.from_private_bytes(_base64url_decode(jwk["d"]))
        self.key_id = jwk.get("kid", "compute-jwk-thumbprint")
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        signer = HTTPMessageSigner(signature_algorithm=algorithms.ED25519,
                                   key_resolver=SingleKeyResolver(self.private_key))
        created = datetime.now(timezone.utc)
        expires = created + timedelta(minutes=5)

        signer.sign(
            request,
            key_id=self.key_id,
            covered_component_ids=("@authority", "signature-agent"),
            created=created,
            expires=expires,
            tag="web-bot-auth",
        )

        return super().send(request, **kwargs)

def get_signed_session():
    s = requests.Session()
    s.mount("https://", WebBotAuthAdapter())
    s.mount("http://", WebBotAuthAdapter())
    return s