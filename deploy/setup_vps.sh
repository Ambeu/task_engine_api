#!/bin/bash
# =============================================================
#  SETUP VPS - Task Engine
#  Ubuntu 22.04 LTS
#  Lancer en root : bash setup_vps.sh
# =============================================================

set -e

APP_USER="taskengine"
APP_DIR="/opt/task_engine"
PYTHON_VERSION="3.12"

echo "=== 1. Mise a jour du systeme ==="
apt update && apt upgrade -y
apt install -y git curl wget unzip ufw fail2ban

echo "=== 2. Installation Python $PYTHON_VERSION ==="
apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev python3-pip

echo "=== 3. Installation Redis ==="
apt install -y redis-server
systemctl enable redis-server
systemctl start redis-server
# Securiser Redis : ecoute uniquement en local
sed -i 's/^bind .*/bind 127.0.0.1/' /etc/redis/redis.conf
sed -i 's/^# requirepass .*/requirepass CHANGE_MOI_REDIS_PASSWORD/' /etc/redis/redis.conf
systemctl restart redis-server

echo "=== 4. Installation Nginx ==="
apt install -y nginx
systemctl enable nginx

echo "=== 5. Creation utilisateur applicatif ==="
useradd --system --shell /bin/bash --home $APP_DIR --create-home $APP_USER || true

echo "=== 6. Clone du projet ==="
# Remplacer par l'URL de ton depot git
# git clone https://github.com/TON_USER/task_engine.git $APP_DIR
# Pour l'instant, copie manuelle ou rsync depuis le poste local

echo "=== 7. Environnement virtuel ==="
python${PYTHON_VERSION} -m venv $APP_DIR/.venv
$APP_DIR/.venv/bin/pip install --upgrade pip
$APP_DIR/.venv/bin/pip install -r $APP_DIR/requirements.txt
$APP_DIR/.venv/bin/pip install gunicorn

echo "=== 8. Permissions ==="
chown -R $APP_USER:$APP_USER $APP_DIR

echo "=== 9. Firewall ==="
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw --force enable

echo ""
echo "=== SETUP TERMINE ==="
echo "Etapes suivantes :"
echo "  1. Editer /etc/task_engine.env avec tes variables"
echo "  2. Copier les fichiers systemd : bash deploy/install_services.sh"
echo "  3. Copier la config Nginx     : bash deploy/install_nginx.sh TON_DOMAINE"
echo "  4. Installer SSL              : certbot --nginx -d TON_DOMAINE"
