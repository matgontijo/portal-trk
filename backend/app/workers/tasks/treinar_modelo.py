# backend/app/workers/tasks/treinar_modelo.py
# Task Celery para re-treinamento do modelo ML.
# Executa toda segunda 03:00 ou manualmente pelo admin.

import structlog

from app.workers.celery_app import celery

logger = structlog.get_logger()


@celery.task(name="app.workers.tasks.treinar_modelo.treinar_modelo_task")
def treinar_modelo_task(user_id: str | None = None):
    """Re-treina o modelo de conciliação ML."""
    import asyncio
    from app.db.session import async_session_factory
    from app.services.ml_conciliacao import MLConciliador

    async def _treinar():
        async with async_session_factory() as db:
            resultado = await MLConciliador.treinar(db, user_id)
            await db.commit()
            return resultado

    try:
        resultado = asyncio.run(_treinar())
        logger.info("ml_treinamento_resultado", **resultado)
        return resultado
    except Exception as e:
        logger.error("ml_treinamento_erro", erro=str(e))
        raise
