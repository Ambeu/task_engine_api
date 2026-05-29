import os
from celery import Celery
from kombu import Queue, Exchange

# Dev local : SQLite (aucune dépendance externe)
# Production : définir les variables d'environnement
BROKER_URL      = os.getenv("CELERY_BROKER_URL",      "sqla+sqlite:///celery_broker.db")
RESULT_BACKEND  = os.getenv("CELERY_RESULT_BACKEND",  "db+sqlite:///celery_results.db")

app = Celery("task_engine", include=["tasks.generic", "tasks.notifier_tasks"])

app.config_from_object({
    "broker_url":     BROKER_URL,
    "result_backend": RESULT_BACKEND,

    "task_serializer":   "json",
    "result_serializer": "json",
    "accept_content":    ["json"],
    "timezone":          "Africa/Abidjan",
    "enable_utc":        True,

    "task_queues": (
        Queue("default",        Exchange("default"), routing_key="default"),
        Queue("haute_priorite", Exchange("haute"),   routing_key="haute"),
        Queue("basse_priorite", Exchange("basse"),   routing_key="basse"),
        Queue("emails",         Exchange("emails"),  routing_key="email"),
        Queue("reports",        Exchange("reports"), routing_key="report"),
    ),
    "task_default_queue":       "default",
    "task_default_exchange":    "default",
    "task_default_routing_key": "default",

    "task_routes": {
        "task.execute":   {"queue": "default"},
        "tasks.urgent.*": {"queue": "haute_priorite"},
        "tasks.batch.*":  {"queue": "basse_priorite"},
    },

    "worker_concurrency":        1,   # solo pool = 1 seul process
    "worker_prefetch_multiplier": 1,

    "task_acks_late":           True,
    "task_reject_on_worker_lost": True,
    "task_time_limit":          3600, # timeout dur uniquement (soft non supporté Windows)

    "result_expires":    86400,
    "result_persistent": True,
})
