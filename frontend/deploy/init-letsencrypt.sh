#!/bin/sh
set -eu

DOMAIN="$1"
EMAIL="$2"

cd "$(dirname "$0")/../.."

docker compose stop nginx >/dev/null 2>$1 || true

docker compose run --rm -p 80:80 --entrypoint certbot certbot certonly \
  --standalone \
  --cert-name trip -d "$DOMAIN" --email "$EMAIL" \
  --agree-tos --no-eff-email

docker compose up -d --remove-orphans

echo "Готово https://$DOMAIN"