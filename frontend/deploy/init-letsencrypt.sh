#!/bin/sh
set -eu

DOMAIN="$1"
EMAIL="$2"

docker compose run --rm --user root --entrypoint "\
  sh -c 'rm -rf /etc/letsencrypt/live/trip && \
         mkdir -p /etc/letsencrypt/live/trip && \
         openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
           -keyout /etc/letsencrypt/live/trip/privkey.pem \
           -out /etc/letsencrypt/live/trip/fullchain.pem \
           -subj /CN=localhost'" certbot

docker compose up -d --remove-orphans
sleep 5

docker compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    --cert-name trip -d \"$DOMAIN\" --email \"$EMAIL\" \
    --agree-tos --no-eff-email --force-renewal" certbot

docker compose exec nginx nginx -s reload

echo "Готово https://$DOMAIN"