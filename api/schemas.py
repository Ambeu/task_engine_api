from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class TaskSubmitRequest(BaseModel):
    task_name: str = Field(
        ...,
        description="Label libre identifiant le type de tâche (ex: geo.position, crm.contact, facture.generer)"
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Données quelconques à traiter — structure libre selon le projet"
    )
    handler_url: Optional[str] = Field(
        None,
        description="URL du service métier qui traite le payload. Sans handler_url, le payload est juste stocké."
    )
    callback_url: Optional[str] = Field(
        None,
        description="URL appelée automatiquement avec le résultat après exécution (webhook)"
    )
    queue: Optional[str] = Field(
        None,
        description="Queue cible : default | haute_priorite | basse_priorite | emails | reports"
    )
    priority: int = Field(default=5, ge=0, le=9, description="Priorité : 0 (basse) à 9 (haute)")
    countdown: int = Field(default=0, ge=0, description="Délai en secondes avant d'exécuter")
    expires: Optional[int] = Field(None, description="Expiration en secondes")
    app_source: str = Field(default="unknown", description="Identifiant de l'application émettrice")


class TaskSubmitResponse(BaseModel):
    task_id: str
    task_name: str
    queue: str
    status: str
    message: str
    handler_url: Optional[str] = None
    callback_url: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    task_name: str
    app_source: str
    queue: str
    status: str
    payload: dict[str, Any]
    handler_url: Optional[str]
    result: Optional[Any]
    error: Optional[str]
    priority: int
    callback_url: Optional[str]
    callback_status: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
