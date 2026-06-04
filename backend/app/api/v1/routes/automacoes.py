# backend/app/api/v1/routes/automacoes.py
# CRUD de automações (gatilho → condição → ação) + simulador de condição.
# Restrito a admin/gestor.

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import DbSession, get_current_user, require_role
from app.db.models.automacao import ACOES, GATILHOS, Automacao
from app.schemas.automacao import (
    AutomacaoCreate,
    AutomacaoResponse,
    AutomacaoUpdate,
    TestarAutomacaoRequest,
    TestarAutomacaoResponse,
)
from app.services.automacoes import avaliar_condicao

router = APIRouter()


@router.get("/meta")
async def meta(current_user=Depends(get_current_user)):
    """Lista gatilhos e ações disponíveis (para montar o builder no front)."""
    return {
        "gatilhos": list(GATILHOS),
        "acoes": list(ACOES),
        "operadores": ["==", "!=", ">", ">=", "<", "<=", "contains", "in"],
        "campos_por_gatilho": {
            "saldo_divergencia": ["delta", "delta_abs", "saldo_banco", "saldo_omie", "tipo_divergencia", "empresa_nome"],
            "saldo_atualizado": ["saldo_banco", "saldo_omie", "empresa_nome"],
            "saldo_falha": ["empresa_nome", "erro"],
            "rotina_atrasada": ["rotina_nome", "user_id"],
            "rotina_concluida": ["rotina_nome", "user_id"],
            "tarefa_criada": ["titulo", "prioridade"],
        },
    }


@router.get("/", response_model=list[AutomacaoResponse])
async def listar(db: DbSession, current_user=Depends(require_role(["admin", "gestor"]))):
    result = await db.execute(select(Automacao).order_by(Automacao.prioridade.desc(), Automacao.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=AutomacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    payload: AutomacaoCreate,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    if payload.gatilho not in GATILHOS:
        raise HTTPException(422, f"Gatilho inválido. Use um de: {', '.join(GATILHOS)}")
    if payload.acao not in ACOES:
        raise HTTPException(422, f"Ação inválida. Use uma de: {', '.join(ACOES)}")
    auto = Automacao(**payload.model_dump(), created_by=current_user.id)
    db.add(auto)
    await db.commit()
    await db.refresh(auto)
    return auto


@router.put("/{automacao_id}", response_model=AutomacaoResponse)
async def atualizar(
    automacao_id: UUID,
    payload: AutomacaoUpdate,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    auto = await db.get(Automacao, automacao_id)
    if not auto:
        raise HTTPException(404, "Automação não encontrada")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(auto, campo, valor)
    await db.commit()
    await db.refresh(auto)
    return auto


@router.delete("/{automacao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(
    automacao_id: UUID,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    auto = await db.get(Automacao, automacao_id)
    if not auto:
        raise HTTPException(404, "Automação não encontrada")
    await db.delete(auto)
    await db.commit()


@router.post("/testar", response_model=TestarAutomacaoResponse)
async def testar(
    payload: TestarAutomacaoRequest,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Simula a avaliação da condição contra um contexto — sem executar a ação."""
    return TestarAutomacaoResponse(
        condicao_satisfeita=avaliar_condicao(payload.condicao, payload.contexto)
    )
