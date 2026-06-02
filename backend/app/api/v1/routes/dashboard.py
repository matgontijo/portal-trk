# backend/app/api/v1/routes/dashboard.py
# Rotas do dashboard financeiro do Portal TRK.

from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.core.dependencies import DbSession, get_current_user
from app.db.models.lancamento import LancamentoOmie
from app.db.models.saldo import Saldo
from app.schemas.saldo import DashboardKPIs

router = APIRouter()


@router.get("/kpis", response_model=DashboardKPIs)
async def kpis(
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """KPIs do dashboard financeiro consolidado."""
    hoje = date.today()

    # Total em caixa (soma dos últimos saldos de cada empresa)
    subq = (
        select(Saldo.empresa_id, func.max(Saldo.synced_at).label("max_sync"))
        .group_by(Saldo.empresa_id).subquery()
    )
    result = await db.execute(
        select(func.coalesce(func.sum(Saldo.saldo_banco), 0)).join(
            subq,
            (Saldo.empresa_id == subq.c.empresa_id) &
            (Saldo.synced_at == subq.c.max_sync)
        )
    )
    total_caixa = result.scalar() or Decimal("0")

    # A pagar hoje
    result = await db.execute(
        select(func.coalesce(func.sum(LancamentoOmie.valor), 0))
        .where(LancamentoOmie.data_vencimento == hoje)
    )
    a_pagar_hoje = result.scalar() or Decimal("0")

    # A pagar esta semana
    fim_semana = hoje + timedelta(days=7)
    result = await db.execute(
        select(func.coalesce(func.sum(LancamentoOmie.valor), 0))
        .where(
            LancamentoOmie.data_vencimento >= hoje,
            LancamentoOmie.data_vencimento <= fim_semana,
        )
    )
    a_pagar_semana = result.scalar() or Decimal("0")

    # Em atraso
    result = await db.execute(
        select(func.coalesce(func.sum(LancamentoOmie.valor), 0))
        .where(
            LancamentoOmie.data_vencimento < hoje,
            LancamentoOmie.status_omie != "liquidado",
        )
    )
    em_atraso = result.scalar() or Decimal("0")

    # Empresas com divergência
    result = await db.execute(
        select(func.count(func.distinct(Saldo.empresa_id)))
        .join(subq, (Saldo.empresa_id == subq.c.empresa_id) & (Saldo.synced_at == subq.c.max_sync))
        .where(Saldo.tem_divergencia == True)
    )
    divergentes = result.scalar() or 0

    # Total empresas
    from app.db.models.empresa import Empresa
    result = await db.execute(select(func.count()).where(Empresa.is_active == True))
    total_empresas = result.scalar() or 0

    return DashboardKPIs(
        total_em_caixa=total_caixa,
        a_pagar_hoje=a_pagar_hoje,
        a_pagar_semana=a_pagar_semana,
        em_atraso=em_atraso,
        empresas_com_divergencia=divergentes,
        total_empresas=total_empresas,
    )


@router.get("/equipe-progresso")
async def progresso_equipe(
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """Progresso da equipe no dia (gestor vê todos, funcionário vê o seu)."""
    from app.db.models.rotina_progresso import RotinaProgresso
    from app.db.models.user import User

    hoje = date.today()

    query = (
        select(
            User.id, User.name,
            func.count(RotinaProgresso.id).label("total"),
            func.count(RotinaProgresso.id).filter(RotinaProgresso.is_done == True).label("concluidos"),
        )
        .join(RotinaProgresso, RotinaProgresso.user_id == User.id)
        .where(RotinaProgresso.data_referencia == hoje)
        .group_by(User.id, User.name)
    )

    if current_user.role == "funcionario":
        query = query.where(User.id == current_user.id)

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "user_id": str(row.id),
            "user_name": row.name,
            "total": row.total,
            "concluidos": row.concluidos,
            "percentual": round(row.concluidos / row.total * 100, 1) if row.total > 0 else 0,
        }
        for row in rows
    ]
