# backend/app/workers/tasks/conciliacao_auto.py
# Task Celery para conciliação automática pós-sync.
# Roda a ConciliacaoEngine (regras + ML) para cada empresa ativa.
# A engine é assíncrona; o Celery é síncrono — por isso usamos asyncio.run.

import asyncio

import structlog

from app.workers.celery_app import celery

logger = structlog.get_logger()


@celery.task(name="app.workers.tasks.conciliacao_auto.conciliar_todas")
def conciliar_todas():
    """Executa conciliação para todas as empresas ativas."""
    return asyncio.run(_conciliar_todas_async())


@celery.task(name="app.workers.tasks.conciliacao_auto.conciliar_empresa_task")
def conciliar_empresa_task(empresa_id: str):
    """Conciliação manual de uma empresa (disparada pela UI)."""
    from uuid import UUID
    return asyncio.run(_conciliar_empresa_async(UUID(empresa_id)))


async def _conciliar_todas_async() -> dict:
    from sqlalchemy import select
    from app.db.models.empresa import Empresa
    from app.db.session import async_session_factory

    total_matches = 0
    empresas_ok = 0
    async with async_session_factory() as db:
        empresas = (
            await db.execute(select(Empresa).where(Empresa.is_active == True))  # noqa: E712
        ).scalars().all()
        logger.info("conciliacao_auto_iniciada", total=len(empresas))

        for empresa in empresas:
            matches = await _conciliar_uma(db, empresa)
            if matches is not None:
                empresas_ok += 1
                total_matches += matches

    logger.info("conciliacao_auto_concluida", empresas=empresas_ok, matches=total_matches)
    return {"empresas": empresas_ok, "matches": total_matches}


async def _conciliar_empresa_async(empresa_id) -> dict:
    from app.db.models.empresa import Empresa
    from app.db.session import async_session_factory

    async with async_session_factory() as db:
        empresa = await db.get(Empresa, empresa_id)
        if not empresa:
            return {"status": "nao_encontrada"}
        matches = await _conciliar_uma(db, empresa)
        return {"status": "ok" if matches is not None else "erro", "matches": matches or 0}


async def _conciliar_uma(db, empresa) -> int | None:
    """Concilia uma empresa em transação isolada. Retorna nº de matches ou None em erro."""
    from app.services.conciliacao import ConciliacaoEngine

    try:
        engine = ConciliacaoEngine(db, empresa.id)
        stats = await engine.executar()
        await db.commit()
        matches = stats.get("matches_fase1", 0) + stats.get("matches_fase2", 0)
        logger.info("conciliacao_empresa_ok", empresa=empresa.nome, matches=matches)
        return matches
    except Exception as e:  # noqa: BLE001
        await db.rollback()
        logger.error("conciliacao_empresa_erro", empresa=getattr(empresa, "nome", "?"), erro=str(e))
        return None
