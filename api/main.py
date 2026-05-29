from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from core.database import init_db
from api.routes.tasks import router as tasks_router
from api.routes.queues import router as queues_router

PDF_PATH = Path(__file__).parent.parent / "task_engine_documentation.pdf"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task Engine API",
    description=(
        "Moteur d'exécution de tâches distribué.\n\n"
        "Les applications externes soumettent des tâches via `POST /tasks/submit`. "
        "Les workers Celery les exécutent. Le statut est consultable via `GET /tasks/{id}`."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(tasks_router)
app.include_router(queues_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Task Engine",
        "status": "running",
        "docs": "/docs",
        "available_tasks": "/tasks/available",
        "documentation": "/documentation",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.get("/documentation", tags=["Health"], response_class=FileResponse)
def get_documentation():
    if not PDF_PATH.exists():
        raise HTTPException(status_code=404, detail="PDF introuvable. Lancez generate_doc.py d'abord.")
    return FileResponse(
        path=str(PDF_PATH),
        media_type="application/pdf",
        filename="task_engine_documentation.pdf",
    )
