import uuid
from datetime import datetime, timezone
from typing import Optional

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas import TaskSubmitRequest, TaskSubmitResponse, TaskResponse
from celery_app import app as celery_app
from core.database import get_db
from core.models import TaskRecord

router = APIRouter(prefix="/tasks", tags=["Tasks"])

QUEUES = {"default", "haute_priorite", "basse_priorite", "emails", "reports"}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _sync_status(record: TaskRecord, db: Session) -> TaskRecord:
    async_result = AsyncResult(record.id, app=celery_app)
    celery_status = async_result.state

    if celery_status != record.status:
        record.status = celery_status
        record.updated_at = _now()
        if celery_status == "FAILURE":
            record.error = str(async_result.result)
        db.commit()

    return record


# ──────────────────────────────────────────────
# POST /tasks/submit
# ──────────────────────────────────────────────
@router.post("/submit", response_model=TaskSubmitResponse, status_code=201)
def submit_task(payload: TaskSubmitRequest, db: Session = Depends(get_db)):
    queue = payload.queue or "default"
    if queue not in QUEUES:
        raise HTTPException(status_code=400, detail=f"Queue invalide. Valeurs possibles : {sorted(QUEUES)}")

    task_id = str(uuid.uuid4())

    send_kwargs: dict = {
        "task_id": task_id,
        "kwargs": {
            "task_name":    payload.task_name,
            "payload":      payload.payload,
            "task_id":      task_id,
            "handler_url":  payload.handler_url,
            "callback_url": payload.callback_url,
        },
        "queue":    queue,
        "priority": payload.priority,
    }
    if payload.countdown:
        send_kwargs["countdown"] = payload.countdown
    if payload.expires:
        send_kwargs["expires"] = payload.expires

    celery_app.send_task("task.execute", **send_kwargs)

    now = _now()
    record = TaskRecord(
        id=task_id,
        app_source=payload.app_source,
        task_name=payload.task_name,
        queue=queue,
        payload=payload.payload,
        handler_url=payload.handler_url,
        status="PENDING",
        priority=payload.priority,
        callback_url=payload.callback_url,
        callback_status="PENDING" if payload.callback_url else None,
        created_at=now,
        updated_at=now,
    )
    db.add(record)
    db.commit()

    return TaskSubmitResponse(
        task_id=task_id,
        task_name=payload.task_name,
        queue=queue,
        status="PENDING",
        handler_url=payload.handler_url,
        callback_url=payload.callback_url,
        message=f"Tâche '{payload.task_name}' soumise dans la queue '{queue}'.",
    )


# ──────────────────────────────────────────────
# GET /tasks/
# ──────────────────────────────────────────────
@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    app_source: Optional[str] = None,
    task_name: Optional[str] = None,
    status: Optional[str] = None,
    queue: Optional[str] = None,
    callback_status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(TaskRecord)
    if app_source:
        query = query.filter(TaskRecord.app_source == app_source)
    if task_name:
        query = query.filter(TaskRecord.task_name == task_name)
    if status:
        query = query.filter(TaskRecord.status == status)
    if queue:
        query = query.filter(TaskRecord.queue == queue)
    if callback_status:
        query = query.filter(TaskRecord.callback_status == callback_status)
    return query.order_by(TaskRecord.created_at.desc()).limit(limit).all()


# ──────────────────────────────────────────────
# GET /tasks/{task_id}
# ──────────────────────────────────────────────
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    record = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")
    return _sync_status(record, db)


# ──────────────────────────────────────────────
# POST /tasks/{task_id}/resend
# ──────────────────────────────────────────────
@router.post("/{task_id}/resend", status_code=202)
def resend_callback(task_id: str, db: Session = Depends(get_db)):
    record = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")
    if not record.callback_url:
        raise HTTPException(status_code=400, detail="Aucun callback_url configuré pour cette tâche.")
    if record.status != "SUCCESS":
        raise HTTPException(
            status_code=400,
            detail=f"La tâche doit être SUCCESS pour renvoyer le callback (statut : {record.status})."
        )

    celery_app.send_task(
        "tasks.notifier_tasks.envoyer_callback",
        kwargs={"task_result": record.result, "callback_url": record.callback_url, "task_id": task_id},
    )
    record.callback_status = "PENDING"
    record.updated_at = _now()
    db.commit()

    return {"task_id": task_id, "callback_url": record.callback_url, "message": "Callback resoumis."}


# ──────────────────────────────────────────────
# DELETE /tasks/{task_id}
# ──────────────────────────────────────────────
@router.delete("/{task_id}")
def cancel_task(task_id: str, terminate: bool = False, db: Session = Depends(get_db)):
    record = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Tâche introuvable.")

    AsyncResult(task_id, app=celery_app).revoke(terminate=terminate, signal="SIGTERM")
    record.status = "REVOKED"
    record.updated_at = _now()
    db.commit()

    return {"task_id": task_id, "status": "REVOKED", "message": "Tâche révoquée."}
