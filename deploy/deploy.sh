#!/bin/bash
# =============================================================
#  MISE A JOUR DU CODE EN PRODUCTION
#  A lancer a chaque nouveau deploiement
# =============================================================

set -e

APP_DIR="/opt/task_engine"

echo "=== Pull du code ==="
cd $APP_DIR
git pull origin main

echo "=== Mise a jour des dependances ==="
$APP_DIR/.venv/bin/pip install -r requirements.txt --quiet

echo "=== Regeneration du PDF ==="
cd $APP_DIR
$APP_DIR/.venv/bin/python generate_doc.py

echo "=== Redemarrage des services ==="
systemctl restart task-engine-api
systemctl restart task-engine-worker

echo "=== Verification ==="
sleep 3
systemctl is-active task-engine-api    && echo "API    : OK" || echo "API    : ERREUR"
systemctl is-active task-engine-worker && echo "Worker : OK" || echo "Worker : ERREUR"

echo ""
echo "Deploiement termine."
