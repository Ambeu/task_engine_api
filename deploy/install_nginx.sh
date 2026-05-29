#!/bin/bash
# =============================================================
#  Installation Nginx + SSL Let's Encrypt
#  Usage : bash install_nginx.sh api.mondomaine.com
# =============================================================

set -e

DOMAINE=${1:?"Usage: bash install_nginx.sh TON_DOMAINE"}
APP_DIR="/opt/task_engine"

echo "=== Configuration Nginx pour $DOMAINE ==="
sed "s/TON_DOMAINE/$DOMAINE/g" $APP_DIR/deploy/nginx.conf \
    > /etc/nginx/sites-available/task_engine

ln -sf /etc/nginx/sites-available/task_engine \
       /etc/nginx/sites-enabled/task_engine

# Supprimer le site par defaut
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx
echo "  -> Nginx configure pour $DOMAINE"

echo "=== Installation SSL avec Certbot ==="
apt install -y certbot python3-certbot-nginx
certbot --nginx -d $DOMAINE --non-interactive --agree-tos \
    --email admin@$DOMAINE --redirect

systemctl reload nginx

echo ""
echo "=== DONE ==="
echo "API accessible sur : https://$DOMAINE"
echo "Docs Swagger       : https://$DOMAINE/docs"
echo "Documentation PDF  : https://$DOMAINE/documentation"
