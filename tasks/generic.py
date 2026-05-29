import httpx
from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    name="task.execute",
    queue="default",
    max_retries=3,
    default_retry_delay=30,
)
def execute(
    self,
    task_name: str,
    payload: dict,
    task_id: str = None,
    handler_url: str = None,
    callback_url: str = None,
) -> dict:
    """
    Tâche universelle — aucun code métier ici.

    Sans handler_url : stocke le payload tel quel (le moteur est un simple entrepôt).
    Avec handler_url : délègue le traitement au service métier et récupère le résultat.
    Avec callback_url : notifie l'app source avec le résultat final.

    Exemples d'utilisation :
        Geo app  → handler_url="http://geo-service/process"
        CRM app  → handler_url="http://crm/contacts/process"
        Billing  → handler_url="http://billing/invoices/generate"
    """
    try:
        if handler_url:
            response = httpx.post(
                handler_url,
                json={"task_id": task_id, "task_name": task_name, "payload": payload},
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"[{task_name}] Traité par {handler_url} → HTTP {response.status_code}")
        else:
            # Pas de handler : stockage brut du payload
            result = {"task_name": task_name, "payload": payload}
            logger.info(f"[{task_name}] Stocké (pas de handler)")

        _persist_result(task_id, result)

        if callback_url:
            from tasks.notifier_tasks import envoyer_callback
            envoyer_callback.apply_async(
                kwargs={"task_result": result, "callback_url": callback_url, "task_id": task_id}
            )

        return result

    except httpx.TimeoutException as exc:
        logger.warning(f"[{task_name}] Timeout handler — retry {self.request.retries + 1}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 30)

    except httpx.HTTPStatusError as exc:
        logger.error(f"[{task_name}] Erreur HTTP {exc.response.status_code} depuis handler")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 30)

    except Exception as exc:
        logger.error(f"[{task_name}] Erreur inattendue : {exc}")
        raise self.retry(exc=exc)


def _persist_result(task_id: str, result: dict) -> None:
    if not task_id:
        return
    try:
        from core.database import SessionLocal
        from core.models import TaskRecord

        db = SessionLocal()
        try:
            record = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
            if record:
                record.result = result
                record.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    except Exception as exc:
        logger.warning(f"Impossible de persister le résultat : {exc}")
