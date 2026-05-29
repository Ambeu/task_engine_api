#!/bin/bash
# =============================================================
#  Installation des services systemd
#  Lancer en root depuis /opt/task_engine
# =============================================================

set -e

APP_DIR="/opt/task_engine"

echo "=== Creation des dossiers de logs ==="
mkdir -p /var/log/task_engine
mkdir -p /var/run/task_engine
chown -R taskengine:taskengine /var/log/task_engine /var/run/task_engine

echo "=== Copie des variables d'environnement ==="
cp $APP_DIR/deploy/task_engine.env /etc/task_engine.env
chmod 600 /etc/task_engine.env
echo "  -> Edite /etc/task_engine.env avec tes vrais mots de passe Redis"

echo "=== Installation des services systemd ==="
cp $APP_DIR/deploy/task-engine-api.service    /etc/systemd/system/
cp $APP_DIR/deploy/task-engine-worker.service /etc/systemd/system/

systemctl daemon-reload

echo "=== Activation au demarrage ==="
systemctl enable task-engine-api
systemctl enable task-engine-worker

echo "=== Demarrage ==="
systemctl start task-engine-api
systemctl start task-engine-worker

echo ""
echo "=== STATUS ==="
systemctl status task-engine-api    --no-pager -l
systemctl status task-engine-worker --no-pager -l

echo ""
echo "Commandes utiles :"
echo "  systemctl status  task-engine-api"
echo "  systemctl restart task-engine-worker"
echo "  journalctl -u task-engine-api    -f"
echo "  journalctl -u task-engine-worker -f"
echo "  tail -f /var/log/task_engine/worker.log"
