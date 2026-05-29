from fastapi import APIRouter
from celery_app import app as celery_app

router = APIRouter(prefix="/queues", tags=["Queues & Workers"])

QUEUES = ["default", "haute_priorite", "basse_priorite", "emails", "reports"]


@router.get("/")
def list_queues():
    return {"queues": QUEUES}


@router.get("/workers")
def workers_stats():
    inspect = celery_app.control.inspect(timeout=3)
    return {
        "active":     inspect.active()    or {},
        "scheduled":  inspect.scheduled() or {},
        "reserved":   inspect.reserved()  or {},
        "stats":      inspect.stats()     or {},
    }


@router.get("/workers/ping")
def ping_workers():
    result = celery_app.control.inspect(timeout=3).ping()
    return {"workers": result or {}}
