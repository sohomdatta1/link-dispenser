#!/bin/sh
set -e
mkdir -p ./keys
go install github.com/nao1215/jose@latest
export PATH=$PATH:$HOME/go/bin
jose jwk generate --type OKP --curve Ed25519 --output-format json -o ./keys/private-key.jwk
# Now that we have the.jwk, we need to upload it to the Toolforge secret manager
# First, base64 encode it, then ssh login.toolforge.org and run:
# toolforge envvars create BOT_AUTH_JWKS_DATA and then paste the base64 data

if [ $# -lt 1 ]; then
    echo "BOT_AUTH_JWKS_DATA not uploaded, instead adding to .env for local dev. Run with 'upload' argument to upload to Toolforge."
    echo "BOT_AUTH_JWKS_DATA=$(base64 -w0 ./keys/private-key.jwk | tr -d '=')" >> .env
else
    ssh login.toolforge.org "become link-dispenser toolforge envvars create BOT_AUTH_JWKS_DATA $(base64 -w0 ./keys/private-key.jwk)"
    echo "Keys created and uploaded. Keep private-key.pem safe!"
fi