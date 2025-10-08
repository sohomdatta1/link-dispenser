#!/bin/bash
mkdir -p /tmp && \
printf '%s' "$BOT_AUTH_JWKS_DATA" | base64 --decode > /tmp/bot_auth.jwks.json && \
export BOT_AUTH_JWKS_FILE=/tmp/bot_auth.jwks.json
export PYTHONUNBUFFERED=TRUE
gunicorn -w 4 -b 0.0.0.0 router:app --timeout 600 --access-logfile -