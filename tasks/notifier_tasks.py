import httpx
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    name="tasks.notifier_tasks.envoyer_callback",
    queue="default",
    max_retries=5,
    default_retry_delay=30,
)
def envoyer_callback(self, task_result: dict, callback_url: str, task_id: str) -> dict:
    """
    Reçoit le résultat d'une tâche et le POSTe à l'URL de callback de l'application source.
    Chaîné automatiquement via Celery link après l'exécution de la tâche principale.
    """
    try:
        payload = {
            "task_id":      task_id,
            "status":       "SUCCESS",
            "result":       task_result,
            "tentative":    self.request.retries + 1,
        }

        response = httpx.post(callback_url, json=payload, timeout=10)
        response.raise_for_status()

        logger.info(f"Callback envoyé → {callback_url} [{response.status_code}]")
        _update_callback_status(task_id, "SENT")

        return {
            "callback_url": callback_url,
            "http_status":  response.status_code,
            "status":       "SENT",
        }

    except httpx.TimeoutException as exc:
        logger.warning(f"Timeout callback {callback_url} — retry {self.request.retries + 1}")
        _update_callback_status(task_id, "RETRYING")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 30)

    except httpx.HTTPStatusError as exc:
        logger.error(f"Erreur HTTP {exc.response.status_code} pour {callback_url}")
        _update_callback_status(task_id, "FAILED")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 30)

    except Exception as exc:
        logger.error(f"Erreur callback inattendue : {exc}")
        _update_callback_status(task_id, "FAILED")
        raise self.retry(exc=exc)


def _update_callback_status(task_id: str, status: str) -> None:
    try:
        from core.database import SessionLocal
        from core.models import TaskRecord
        from datetime import datetime

        db = SessionLocal()
        try:
            record = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
            if record:
                record.callback_status = status
                record.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    except Exception as exc:
        logger.warning(f"Impossible de mettre à jour callback_status : {exc}")
