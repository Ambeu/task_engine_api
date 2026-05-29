from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
def ascii_safe(text: str) -> str:
    """Remplace les caractères hors latin-1 par des équivalents ASCII."""
    replacements = {
        "—": "-", "–": "-", "‒": "-",
        "→": "->", "←": "<-", "⇒": "=>",
        "►": "->", "▼": "v", "▶": ">",
        "│": "|", "┃": "|",
        "┌": "+", "┐": "+", "└": "+", "┘": "+",
        "├": "+", "┤": "+", "┬": "+", "┴": "+",
        "┼": "+",
        "─": "-", "━": "-", "═": "=",
        "•": "-", "‣": "-", "⁃": "-",
        "●": "*", "○": "o",
        "✓": "OK", "✔": "OK", "✕": "X", "✖": "X",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a", "ä": "a",
        "î": "i", "ï": "i",
        "ô": "o", "ö": "o",
        "ù": "u", "û": "u", "ü": "u",
        "ç": "c",
        "É": "E", "È": "E", "Ê": "E",
        "À": "A", "Â": "A",
        "Î": "I",
        "Ô": "O",
        "Ù": "U", "Û": "U",
        "Ç": "C",
    }
    result = []
    for ch in text:
        if ch in replacements:
            result.append(replacements[ch])
        elif ord(ch) > 255:
            result.append("?")
        else:
            result.append(ch)
    return "".join(result)

BLEU      = (30,  90,  160)
BLEU_CLAIR= (220, 235, 255)
GRIS_CODE = (40,  44,  52)
BLANC     = (255, 255, 255)
GRIS_TEXTE= (80,  80,  80)
VERT      = (34,  139, 34)
ORANGE    = (200, 100, 0)


class PDF(FPDF):

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*GRIS_TEXTE)
        self.cell(0, 8, "Task Engine API - Documentation", align="L")
        self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*BLEU)
        self.set_line_width(0.3)
        self.line(10, 18, 200, 18)
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*GRIS_TEXTE)
        self.cell(0, 10, ascii_safe(f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}"), align="C")

    def cover(self):
        self.set_fill_color(*BLEU)
        self.rect(0, 0, 210, 120, "F")
        self.set_text_color(*BLANC)
        self.set_font("Helvetica", "B", 32)
        self.set_y(35)
        self.cell(0, 14, "TASK ENGINE API", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 16)
        self.cell(0, 10, "Moteur d'execution de taches distribue", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "I", 11)
        self.cell(0, 8, "Celery + FastAPI + SQLite", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_y(130)
        self.set_text_color(*GRIS_TEXTE)
        self.set_font("Helvetica", "", 10)
        badges = [
            ("Broker",   "SQLite (dev) / Redis (prod)"),
            ("API",      "FastAPI - http://localhost:8000"),
            ("Docs",     "http://localhost:8000/docs"),
            ("Worker",   "Celery --pool=solo"),
        ]
        for label, val in badges:
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*BLEU)
            self.cell(40, 7, label + " :", align="R")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(*GRIS_TEXTE)
            self.cell(0, 7, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def titre_section(self, texte, numero=None):
        self.ln(4)
        self.set_fill_color(*BLEU)
        self.set_text_color(*BLANC)
        self.set_font("Helvetica", "B", 12)
        label = ascii_safe(f"  {numero}. {texte}" if numero else f"  {texte}")
        self.cell(0, 9, label, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)
        self.set_text_color(*GRIS_TEXTE)

    def sous_titre(self, texte):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLEU)
        self.cell(0, 7, ascii_safe(texte), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*GRIS_TEXTE)
        self.ln(1)

    def paragraphe(self, texte):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GRIS_TEXTE)
        self.multi_cell(0, 6, ascii_safe(texte))
        self.ln(1)

    def code(self, texte):
        self.set_fill_color(*GRIS_CODE)
        self.set_text_color(*BLANC)
        self.set_font("Courier", "", 9)
        lignes = texte.strip().split("\n")
        pad = 3
        self.ln(1)
        self.set_x(10)
        h = len(lignes) * 5 + pad * 2
        self.set_fill_color(*GRIS_CODE)
        self.rect(10, self.get_y(), 190, h, "F")
        self.set_y(self.get_y() + pad)
        for ligne in lignes:
            self.set_x(14)
            self.cell(0, 5, ascii_safe(ligne), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(pad)
        self.set_text_color(*GRIS_TEXTE)

    def tableau(self, headers, rows, widths=None):
        if widths is None:
            w = 190 // len(headers)
            widths = [w] * len(headers)

        # En-tête
        self.set_fill_color(*BLEU)
        self.set_text_color(*BLANC)
        self.set_font("Helvetica", "B", 9)
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, ascii_safe(f"  {h}"), border=0, fill=True)
        self.ln()

        # Lignes
        self.set_font("Helvetica", "", 9)
        for j, row in enumerate(rows):
            fill = j % 2 == 0
            self.set_fill_color(*BLEU_CLAIR)
            self.set_text_color(*GRIS_TEXTE)
            for i, cell in enumerate(row):
                self.cell(widths[i], 6, ascii_safe(f"  {cell}"), border=0, fill=fill)
            self.ln()
        self.ln(3)

    def puce(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*GRIS_TEXTE)
        for item in items:
            self.set_x(14)
            self.cell(5, 6, "-")
            self.multi_cell(0, 6, ascii_safe(item))
        self.ln(1)

    def encadre(self, titre, texte, couleur=None):
        if couleur is None:
            couleur = BLEU_CLAIR
        self.set_fill_color(*couleur)
        self.set_draw_color(*BLEU)
        self.set_line_width(0.3)
        x, y = self.get_x(), self.get_y()
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*BLEU)
        self.cell(0, 6, ascii_safe(f"  {titre}"), fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GRIS_TEXTE)
        self.set_fill_color(245, 248, 255)
        self.multi_cell(0, 5, ascii_safe(f"  {texte}"), fill=True)
        self.ln(2)


# -------------------------------------------------------------
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.set_margins(10, 10, 10)

# -- PAGE DE COUVERTURE ----------------------------------------
pdf.add_page()
pdf.cover()

# -- PAGE 2 : SOMMAIRE -----------------------------------------
pdf.add_page()
pdf.titre_section("TABLE DES MATIÈRES")
sommaire = [
    ("1", "Architecture du projet"),
    ("2", "Démarrage rapide"),
    ("3", "Concepts clés : handler_url et callback_url"),
    ("4", "Flux d'exécution complet"),
    ("5", "Endpoints API"),
    ("6", "Statuts des tâches"),
    ("7", "Structure des fichiers"),
    ("8", "Ajouter un nouveau projet"),
    ("9", "Exemples de soumission"),
    ("10", "Passer en production"),
]
pdf.set_font("Helvetica", "", 11)
for num, titre in sommaire:
    pdf.set_text_color(*BLEU)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(10, 8, num + ".")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*GRIS_TEXTE)
    pdf.cell(0, 8, titre, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# -- PAGE 3 : ARCHITECTURE -------------------------------------
pdf.add_page()
pdf.titre_section("Architecture du projet", "1")
pdf.paragraphe(
    "Le Task Engine est un moteur d'exécution de tâches asynchrones universel. "
    "Il reçoit des tâches de n'importe quelle application externe via une API REST, "
    "les exécute via des workers Celery, et notifie les applications des résultats."
)

pdf.sous_titre("Structure des composants")
pdf.code("""
App Externe (CRM, GEO, Facturation...)
        |
        |  POST /tasks/submit  { payload, handler_url, callback_url }
        v
+-----------------------------┐
|     FastAPI  (port 8000)    |  <- Reçoit et enregistre les tâches
|     api/main.py             |
+------------┬----------------┘
             | send_task("task.execute")
             v
+-----------------------------┐
|    Broker SQLite / Redis    |  <- File d'attente des tâches
+------------┬----------------┘
             |
             v
+-----------------------------┐
|    Celery Worker            |  <- Exécute les tâches
|    tasks/generic.py         |
|    tasks/notifier_tasks.py  |
+------------┬----------------┘
             |
             ├--> POST handler_url  (service métier de l'app)
             +--> POST callback_url (notification à l'app)
""")

pdf.sous_titre("Fichiers du projet")
pdf.tableau(
    ["Fichier", "Rôle"],
    [
        ("celery_app.py",              "Configuration Celery (broker, queues, workers)"),
        ("api/main.py",                "Application FastAPI + démarrage DB"),
        ("api/schemas.py",             "Modèles de données (Pydantic)"),
        ("api/routes/tasks.py",        "Endpoints : submit, status, historique, annuler"),
        ("api/routes/queues.py",       "Endpoints : queues, workers stats"),
        ("core/database.py",           "Connexion SQLite + session SQLAlchemy"),
        ("core/models.py",             "Table tasks (SQLAlchemy ORM)"),
        ("tasks/generic.py",           "Tâche universelle task.execute"),
        ("tasks/notifier_tasks.py",    "Envoi du callback HTTP"),
        ("start.ps1",                  "Script de démarrage (worker + API)"),
    ],
    [75, 115]
)

# -- PAGE 4 : DÉMARRAGE ----------------------------------------
pdf.add_page()
pdf.titre_section("Démarrage rapide", "2")

pdf.sous_titre("Prérequis")
pdf.puce([
    "Python 3.12+",
    "Environnement virtuel .venv déjà configuré (pip install -r requirements.txt)",
    "Redis optionnel en production (SQLite utilisé par défaut en dev)",
])

pdf.sous_titre("Lancer le projet (une seule commande)")
pdf.code("""cd C:\\proj_python\\celery_proj
.\\start.ps1""")

pdf.paragraphe("Le script start.ps1 ouvre automatiquement deux fenêtres :")
pdf.puce([
    "Fenêtre Worker  : celery -A celery_app worker --loglevel=info --pool=solo",
    "Fenêtre API     : uvicorn api.main:app --reload --port 8000",
])

pdf.sous_titre("Si start.ps1 est bloqué par la politique PowerShell")
pdf.code("""Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned""")

pdf.sous_titre("Vérifier que le worker est actif")
pdf.code("""GET http://localhost:8000/queues/workers/ping""")
pdf.paragraphe("Réponse attendue : { \"workers\": { \"celery@PC\": { ... } } }")

pdf.sous_titre("Accès Swagger UI")
pdf.paragraphe("Tous les endpoints sont testables graphiquement sur :")
pdf.code("""http://localhost:8000/docs""")

# -- PAGE 5 : HANDLER & CALLBACK ------------------------------
pdf.add_page()
pdf.titre_section("Concepts clés : handler_url et callback_url", "3")

pdf.sous_titre("handler_url - Qui traite les données ?")
pdf.paragraphe(
    "L'URL du service métier de ton application qui reçoit le payload et effectue "
    "le vrai traitement (enregistrement BDD, calculs, envoi email, etc.). "
    "Le moteur ne connaît pas la logique métier - il délègue simplement."
)
pdf.code("""Worker -> POST handler_url
         Body : { "task_id": "...", "task_name": "geo.position", "payload": {...} }
         <- Réponse JSON du service (résultat du traitement)""")

pdf.sous_titre("callback_url - Qui est notifié quand c'est fini ?")
pdf.paragraphe(
    "L'URL appelée automatiquement après l'exécution complète de la tâche. "
    "Permet à l'application source de recevoir le résultat sans interroger l'API en boucle."
)
pdf.code("""Worker (terminé) -> POST callback_url
         Body : {
           "task_id":   "fe99bc03-...",
           "status":    "SUCCESS",
           "result":    { ... résultat ... },
           "tentative": 1
         }""")

pdf.sous_titre("Les 4 combinaisons possibles")
pdf.tableau(
    ["handler_url", "callback_url", "Comportement"],
    [
        ("Non",  "Non",  "Stockage brut du payload. Interroger GET /tasks/{id}."),
        ("Non",  "Oui",  "Stockage + notification de l'app avec le payload."),
        ("Oui",  "Non",  "Délégation au service métier. Interroger GET /tasks/{id}."),
        ("Oui",  "Oui",  "Délégation + notification avec le résultat. Mode complet."),
    ],
    [30, 30, 130]
)

pdf.encadre(
    "Conseil",
    "Pour tester les callbacks sans service réel, utiliser https://webhook.site "
    "qui génère une URL unique et affiche les requêtes reçues en temps réel."
)

# -- PAGE 6 : FLUX COMPLET -------------------------------------
pdf.add_page()
pdf.titre_section("Flux d'exécution complet", "4")

pdf.sous_titre("Scénario : soumission avec handler_url + callback_url")
pdf.code("""1. App externe  ->  POST /tasks/submit
              {
                "task_name":    "geo.position",
                "payload":      { "utilisateur_id": "USR-001", "latitude": 5.31 },
                "handler_url":  "http://geo-service/process",
                "callback_url": "http://geo-app/webhook",
                "app_source":   "geo-tracker-app"
              }

2. API          ->  Génère un task_id UUID
               ->  Enregistre en DB (status = PENDING)
               ->  Envoie "task.execute" dans le broker Celery
               ->  Retourne { "task_id": "abc-123", "status": "PENDING" }

3. Worker       ->  Reçoit la tâche (status -> STARTED)
               ->  POST http://geo-service/process avec le payload
               ->  Reçoit le résultat du service métier
               ->  Sauvegarde le résultat en DB (status -> SUCCESS)
               ->  Lance envoyer_callback en arrière-plan

4. Notifier     ->  POST http://geo-app/webhook
               {
                 "task_id": "abc-123",
                 "status":  "SUCCESS",
                 "result":  { ... résultat du service ... }
               }
               ->  callback_status -> SENT""")

pdf.sous_titre("Retry automatique en cas d'échec")
pdf.tableau(
    ["Tentative", "Délai avant retry", "Comportement"],
    [
        ("1", "immédiat",  "Première exécution"),
        ("2", "30 sec",    "Retry 1 - erreur réseau ou timeout"),
        ("3", "60 sec",    "Retry 2"),
        ("4", "120 sec",   "Retry 3 - dernier essai"),
        ("5", "-",         "FAILURE - tâche échouée définitivement"),
    ],
    [30, 40, 120]
)

# -- PAGE 7 : ENDPOINTS ---------------------------------------
pdf.add_page()
pdf.titre_section("Endpoints API", "5")

pdf.sous_titre("Tâches")
pdf.tableau(
    ["Méthode", "Endpoint", "Description"],
    [
        ("POST",   "/tasks/submit",          "Soumettre une nouvelle tâche"),
        ("GET",    "/tasks/",                "Lister l'historique (filtres disponibles)"),
        ("GET",    "/tasks/{task_id}",        "Statut + résultat d'une tâche"),
        ("POST",   "/tasks/{task_id}/resend", "Retenter le callback si échoué"),
        ("DELETE", "/tasks/{task_id}",        "Annuler une tâche"),
    ],
    [20, 65, 105]
)

pdf.sous_titre("Filtres disponibles sur GET /tasks/")
pdf.tableau(
    ["Paramètre", "Exemple", "Description"],
    [
        ("app_source",     "geo-tracker-app", "Tâches d'une application spécifique"),
        ("task_name",      "geo.position",    "Tâches d'un type spécifique"),
        ("status",         "FAILURE",         "Tâches par statut"),
        ("queue",          "haute_priorite",  "Tâches d'une queue"),
        ("callback_status","FAILED",           "Callbacks échoués"),
        ("limit",          "50",              "Nombre de résultats (défaut: 50)"),
    ],
    [40, 50, 100]
)

pdf.sous_titre("Queues & Workers")
pdf.tableau(
    ["Méthode", "Endpoint", "Description"],
    [
        ("GET", "/queues/",              "Liste des queues disponibles"),
        ("GET", "/queues/workers",       "Stats des workers actifs"),
        ("GET", "/queues/workers/ping",  "Ping pour vérifier les workers"),
        ("GET", "/health",               "Health check"),
    ],
    [20, 65, 105]
)

pdf.sous_titre("Body de soumission (POST /tasks/submit)")
pdf.code("""{
  "task_name":    "geo.position",        // Label libre - identifie le type de tâche
  "payload":      { ... },               // Données quelconques (structure libre)
  "handler_url":  "http://...",          // Optionnel - URL de traitement métier
  "callback_url": "http://...",          // Optionnel - URL de notification
  "app_source":   "geo-tracker-app",    // Identifiant de l'application source
  "queue":        "default",            // Optionnel : default | haute_priorite | ...
  "priority":     5,                    // 0 (basse) à 9 (haute) - défaut: 5
  "countdown":    0,                    // Délai en secondes avant exécution
  "expires":      null                  // Expiration en secondes (null = jamais)
}""")

# -- PAGE 8 : STATUTS -----------------------------------------
pdf.add_page()
pdf.titre_section("Statuts des tâches", "6")

pdf.sous_titre("Statuts Celery (champ status)")
pdf.tableau(
    ["Statut", "Signification", "Action possible"],
    [
        ("PENDING",  "Soumise, en attente d'un worker",          "Attendre ou vérifier le worker"),
        ("STARTED",  "Worker en cours d'exécution",              "Attendre la fin"),
        ("SUCCESS",  "Exécution réussie",                        "Lire le résultat"),
        ("FAILURE",  "Échec après tous les retries",             "Consulter l'erreur"),
        ("RETRY",    "En attente avant une nouvelle tentative",  "Attendre le retry"),
        ("REVOKED",  "Annulée manuellement",                     "-"),
    ],
    [35, 90, 65]
)

pdf.sous_titre("Statuts du callback (champ callback_status)")
pdf.tableau(
    ["Statut", "Signification"],
    [
        ("null",      "Pas de callback_url configuré"),
        ("PENDING",   "Callback en attente d'envoi"),
        ("SENT",      "Callback envoyé avec succès"),
        ("RETRYING",  "Échec temporaire, retry en cours"),
        ("FAILED",    "Échec définitif du callback"),
    ],
    [35, 155]
)

pdf.sous_titre("Récupérer le statut d'une tâche")
pdf.code("""GET http://localhost:8000/tasks/{task_id}

Réponse :
{
  "id":              "fe99bc03-3542-4571-a811-5e62d42d2a48",
  "task_name":       "geo.position",
  "app_source":      "geo-tracker-app",
  "queue":           "default",
  "status":          "SUCCESS",
  "payload":         { "utilisateur_id": "USR-001", ... },
  "handler_url":     "http://geo-service/process",
  "result":          { ... résultat ... },
  "error":           null,
  "priority":        5,
  "callback_url":    "http://geo-app/webhook",
  "callback_status": "SENT",
  "created_at":      "2026-05-29T08:15:00",
  "updated_at":      "2026-05-29T08:15:02"
}""")

# -- PAGE 9 : AJOUTER UN PROJET --------------------------------
pdf.add_page()
pdf.titre_section("Ajouter un nouveau projet", "8")

pdf.paragraphe(
    "Le moteur est universel : aucun code n'est à modifier pour ajouter un nouveau projet. "
    "Ton application soumet simplement ses tâches via l'API avec le bon task_name."
)

pdf.sous_titre("Étape 1 - Soumettre une tâche")
pdf.code("""POST http://localhost:8000/tasks/submit
{
  "task_name": "mon-projet.mon-action",
  "payload":   { ... tes données ... },
  "app_source": "mon-application"
}""")

pdf.sous_titre("Étape 2 - Exposer un handler dans ton application (optionnel)")
pdf.code("""# Exemple Python / FastAPI côté ton application
@app.post("/api/mon-action/process")
def process(data: dict):
    task_id  = data["task_id"]
    payload  = data["payload"]

    # Traitement métier
    resultat = faire_quelque_chose(payload)

    return {"status": "ok", "resultat": resultat}""")

pdf.sous_titre("Étape 3 - Exposer un webhook pour le callback (optionnel)")
pdf.code("""@app.post("/api/webhook/done")
def on_task_done(data: dict):
    task_id = data["task_id"]
    result  = data["result"]
    status  = data["status"]

    # Notifier l'utilisateur, mettre à jour l'interface, etc.
    return {"ok": True}""")

pdf.sous_titre("Exemple complet - Projet Facturation")
pdf.code("""POST http://localhost:8000/tasks/submit
{
  "task_name":    "facturation.facture.generer",
  "payload": {
    "client_id":    "CLI-0042",
    "commande_id":  "CMD-2026-0187",
    "montant_fcfa": 125000,
    "tva_pct":      18,
    "echeance":     "2026-06-30"
  },
  "handler_url":  "http://billing-service/api/invoices/generate",
  "callback_url": "http://billing-service/api/invoices/on-generated",
  "app_source":   "billing-app",
  "queue":        "haute_priorite",
  "priority":     7
}""")

# -- PAGE 10 : PRODUCTION -------------------------------------
pdf.add_page()
pdf.titre_section("Passer en production", "10")

pdf.sous_titre("Remplacer SQLite par Redis")
pdf.paragraphe("Redis est recommandé en production pour les performances et la fiabilité.")
pdf.code("""# Définir les variables d'environnement avant de lancer
$env:CELERY_BROKER_URL    = "redis://:motdepasse@redis-host:6379/0"
$env:CELERY_RESULT_BACKEND = "redis://:motdepasse@redis-host:6379/1"

# Ou avec Docker
docker run -d --name redis -p 6379:6379 redis:alpine""")

pdf.sous_titre("Lancer plusieurs workers (Linux/Mac)")
pdf.code("""# Worker avec 4 processus parallèles
celery -A celery_app worker --loglevel=info --concurrency=4

# Workers dédiés par queue
celery -A celery_app worker -Q haute_priorite --concurrency=2
celery -A celery_app worker -Q default,basse_priorite --concurrency=4""")

pdf.sous_titre("Queues disponibles")
pdf.tableau(
    ["Queue", "Usage recommandé"],
    [
        ("default",        "Tâches standard - toutes les apps par défaut"),
        ("haute_priorite", "Tâches urgentes - traitement immédiat (priority 8-9)"),
        ("basse_priorite", "Traitements longs, batch, non urgents"),
        ("emails",         "Envois email - rate limit 100/min"),
        ("reports",        "Génération de rapports lourds"),
    ],
    [45, 145]
)

pdf.sous_titre("Monitorer avec Flower (interface web)")
pdf.code("""pip install flower
celery -A celery_app flower --port=5555
# Interface : http://localhost:5555""")

pdf.encadre(
    "Checklist production",
    "1. Utiliser Redis comme broker et result backend\n"
    "2. Configurer au moins 2 workers pour la redondance\n"
    "3. Activer Flower pour le monitoring\n"
    "4. Configurer des alertes sur les tâches FAILURE\n"
    "5. Mettre result_expires à 7 jours max pour éviter la saturation",
    (255, 245, 220)
)

# -- EXPORT ---------------------------------------------------
output = "task_engine_documentation.pdf"
pdf.output(output)
print(f"PDF généré : {output}")
