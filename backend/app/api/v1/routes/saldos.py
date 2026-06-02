# backend/app/api/v1/routes/saldos.py
# Rotas de saldos bancários do Portal TRK.

from datetime import date, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from app.core.dependencies import DbSession, get_current_user, require_role
from app.db.models.saldo import Saldo
from app.schemas.saldo import SaldoHistorico, SaldoResponse

router = APIRouter()


@router.get("/", response_model=list[SaldoResponse])
async def listar_saldos(
    db: DbSession,
    current_user=Depends(get_current_user),
    empresa_id: UUID | None = None,
):
    """Lista últimos saldos de todas as empresas (ou uma específica)."""
    if empresa_id:
        result = await db.execute(
            select(Saldo).where(Saldo.empresa_id == empresa_id)
            .order_by(Saldo.synced_at.desc()).limit(1)
        )
    else:
        # Subquery para pegar o último saldo de cada empresa
        from sqlalchemy import func, distinct
        subq = (
            select(
                Saldo.empresa_id,
                func.max(Saldo.synced_at).label("max_sync"),
            )
            .group_by(Saldo.empresa_id)
            .subquery()
        )
        result = await db.execute(
            select(Saldo).join(
                subq,
                (Saldo.empresa_id == subq.c.empresa_id) &
                (Saldo.synced_at == subq.c.max_sync)
            )
        )

    saldos = result.scalars().all()
    return [
        SaldoResponse(
            id=s.id, empresa_id=s.empresa_id,
            empresa_nome=s.empresa.nome if s.empresa else "",
            saldo_banco=s.saldo_banco, saldo_omie=s.saldo_omie,
            delta=s.delta, tem_divergencia=s.tem_divergencia,
            tipo_divergencia=s.tipo_divergencia,
            data_referencia=s.data_referencia, synced_at=s.synced_at,
        )
        for s in saldos
    ]


@router.get("/{empresa_id}/historico", response_model=list[SaldoHistorico])
async def historico_saldo(
    empresa_id: UUID,
    db: DbSession,
    current_user=Depends(get_current_user),
    dias: int = Query(30, ge=7, le=90),
):
    """Histórico de saldo de uma empresa para gráfico de evolução."""
    data_inicio = date.today() - timedelta(days=dias)
    result = await db.execute(
        select(Saldo)
        .where(Saldo.empresa_id == empresa_id, Saldo.data_referencia >= data_inicio)
        .order_by(Saldo.data_referencia)
    )
    saldos = result.scalars().all()
    return [
        SaldoHistorico(
            data_referencia=s.data_referencia,
            saldo_banco=s.saldo_banco, saldo_omie=s.saldo_omie,
            delta=s.delta, tem_divergencia=s.tem_divergencia,
        )
        for s in saldos
    ]


@router.post("/{empresa_id}/sync")
async def sync_manual(
    empresa_id: UUID,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Aciona sync manual de uma empresa (ignora cache)."""
    # Disparar task Celery
    from app.workers.tasks.sync_saldos import sync_empresa_task
    sync_empresa_task.delay(str(empresa_id))
    return {"message": "Sync iniciado — os dados serão atualizados em breve"}
