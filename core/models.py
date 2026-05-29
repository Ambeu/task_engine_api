from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime, Text, Integer
from core.database import Base


class TaskRecord(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    app_source = Column(String, index=True, default="unknown")
    task_name = Column(String, index=True)        # label libre fourni par l'app
    queue = Column(String, index=True)
    payload = Column(JSON, default=dict)          # données brutes reçues
    handler_url = Column(String, nullable=True)   # URL de traitement métier
    status = Column(String, index=True, default="PENDING")
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    priority = Column(Integer, default=5)
    callback_url = Column(String, nullable=True)
    callback_status = Column(String, nullable=True)  # PENDING | SENT | RETRYING | FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
