#!/bin/sh
set -e
mkdir -p ./keys
openssl genpkey -algorithm ed25519 -out ./keys/private-key.pem
openssl pkey -in ./keys/private-key.pem -pubout -out ./keys/public-key.pem
go install github.com/jphastings/jwker/cmd/jwker@latest
export PATH=$PATH:$HOME/go/bin
jwker ./keys/public-key.pem ./keys/public-key.jwk
# Now that we have the.jwk, we need to upload it to the Toolforge secret manager
# First, base64 encode it, then ssh login.toolforge.org and run:
# toolforge envvars create BOT_AUTH_JWKS_DATA and then paste the base64 data

if [ $# -lt 1 ]; then
    echo "BOT_AUTH_JWKS_DATA not uploaded, instead adding to .env for local dev. Run with 'upload' argument to upload to Toolforge."
    echo "BOT_AUTH_JWKS_DATA=$(base64 -w0 ./keys/public-key.jwk)" >> .env
else
    ssh login.toolforge.org "become link-dispenser toolforge envvars create BOT_AUTH_JWKS_DATA $(base64 -w0 ./keys/public-key.jwk)"
    echo "Keys created and uploaded. Keep private-key.pem safe!"
fi