# backend/app/workers/celery_app.py
# Fábrica do Celery para o Portal TRK.
# Usa Redis como broker e result backend.
# Tasks autodescobertos em app.workers.tasks.*

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery = Celery(
    "portal_trk",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.update(
    # Serialização
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="America/Sao_Paulo",
    enable_utc=True,
    # Concorrência
    worker_concurrency=2,
    worker_max_tasks_per_child=100,
    # Retry
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Resultado expira em 1 hora
    result_expires=3600,
)

# Autodescoberta de tasks
celery.autodiscover_tasks(["app.workers.tasks"])
