# backend/app/api/v1/routes/conciliacao.py
# Rotas de conciliação do Portal TRK.

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select

from app.core.dependencies import DbSession, get_current_user
from app.db.models.conciliacao import Conciliacao
from app.schemas.conciliacao import (
    ConciliacaoEstatisticas,
    ConciliacaoResponse,
    DecisaoMatch,
)

router = APIRouter()


@router.get("/pendentes", response_model=list[ConciliacaoResponse])
async def listar_pendentes(
    db: DbSession,
    current_user=Depends(get_current_user),
    empresa_id: UUID | None = None,
):
    """Lista conciliações pendentes de revisão manual."""
    query = select(Conciliacao).where(
        Conciliacao.status.in_(["pendente", "revisao_manual"])
    )
    if empresa_id:
        query = query.where(Conciliacao.empresa_id == empresa_id)
    query = query.order_by(Conciliacao.created_at.desc())

    result = await db.execute(query)
    concs = result.scalars().all()

    return [
        ConciliacaoResponse(
            id=c.id,
            lancamento_banco=c.lancamento_banco,
            lancamento_omie=c.lancamento_omie,
            empresa_nome=c.empresa.nome if c.empresa else "",
            data_referencia=c.data_referencia,
            status=c.status,
            confidence_score=float(c.confidence_score) if c.confidence_score else None,
            metodo=c.metodo,
            conciliado_por_nome=c.usuario.name if c.usuario else None,
            obs=c.obs,
            created_at=c.created_at,
        )
        for c in concs
    ]


@router.post("/decidir")
async def decidir_match(
    decisao: DecisaoMatch,
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """Funcionário confirma ou rejeita um match sugerido pela IA."""
    from datetime import date

    if decisao.aceitar and decisao.lancamento_omie_id:
        conc = Conciliacao(
            lancamento_banco_id=decisao.lancamento_banco_id,
            lancamento_omie_id=decisao.lancamento_omie_id,
            empresa_id=None,  # Será preenchido pelo service
            data_referencia=date.today(),
            status="ok",
            confidence_score=1.0,
            metodo="manual",
            conciliado_por=current_user.id,
            obs=decisao.obs,
        )
        # Buscar empresa_id do lançamento
        from app.db.models.lancamento import LancamentoBanco
        lb_result = await db.execute(
            select(LancamentoBanco).where(LancamentoBanco.id == decisao.lancamento_banco_id)
        )
        lb = lb_result.scalar_one_or_none()
        if lb:
            conc.empresa_id = lb.empresa_id

        db.add(conc)
        return {"message": "Match confirmado com sucesso"}
    else:
        # Rejeitar: marcar como sem correspondência
        conc = Conciliacao(
            lancamento_banco_id=decisao.lancamento_banco_id,
            lancamento_omie_id=None,
            empresa_id=None,
            data_referencia=date.today(),
            status="sem_correspondencia",
            metodo="manual",
            conciliado_por=current_user.id,
            obs=decisao.obs,
        )
        from app.db.models.lancamento import LancamentoBanco
        lb_result = await db.execute(
            select(LancamentoBanco).where(LancamentoBanco.id == decisao.lancamento_banco_id)
        )
        lb = lb_result.scalar_one_or_none()
        if lb:
            conc.empresa_id = lb.empresa_id
        db.add(conc)
        return {"message": "Marcado como sem correspondência"}


@router.get("/estatisticas", response_model=ConciliacaoEstatisticas)
async def estatisticas(
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """Estatísticas de conciliação para o dashboard."""
    total_ok = await db.execute(select(func.count()).where(Conciliacao.status == "ok"))
    total_pend = await db.execute(select(func.count()).where(Conciliacao.status == "pendente"))
    total_div = await db.execute(select(func.count()).where(Conciliacao.status == "divergente"))
    total_rev = await db.execute(select(func.count()).where(Conciliacao.status == "revisao_manual"))

    ok = total_ok.scalar() or 0
    pend = total_pend.scalar() or 0
    div = total_div.scalar() or 0
    rev = total_rev.scalar() or 0
    total = ok + pend + div + rev

    # Contar por método
    metodo_result = await db.execute(
        select(Conciliacao.metodo, func.count()).group_by(Conciliacao.metodo)
    )
    por_metodo = {row[0]: row[1] for row in metodo_result.all()}

    return ConciliacaoEstatisticas(
        total_conciliados=ok,
        total_pendentes=pend,
        total_divergentes=div,
        total_revisao_manual=rev,
        taxa_automatica=round((ok / total * 100) if total > 0 else 0, 1),
        por_metodo=por_metodo,
    )
