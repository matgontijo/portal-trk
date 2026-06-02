# backend/app/api/v1/routes/tarefas.py
# Rotas de tarefas (Kanban) do Portal TRK.

from datetime import datetime, timezone
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from app.core.dependencies import DbSession, get_current_user, require_role
from app.db.models.tarefa import Tarefa
from app.schemas.tarefa import TarefaCreate, TarefaResponse, TarefaUpdate

router = APIRouter()
logger = structlog.get_logger()


@router.get("/", response_model=list[TarefaResponse])
async def listar_tarefas(
    db: DbSession,
    current_user=Depends(get_current_user),
    status_filtro: str | None = Query(None, alias="status"),
    prioridade: str | None = None,
    atribuido_a: UUID | None = None,
):
    """
    Lista tarefas. Funcionário vê apenas as suas.
    Gestor+ vê todas, com filtros opcionais.
    """
    query = select(Tarefa)

    if current_user.role == "funcionario":
        query = query.where(Tarefa.atribuido_a == current_user.id)
    elif atribuido_a:
        query = query.where(Tarefa.atribuido_a == atribuido_a)

    if status_filtro:
        query = query.where(Tarefa.status == status_filtro)
    if prioridade:
        query = query.where(Tarefa.prioridade == prioridade)

    query = query.order_by(Tarefa.created_at.desc())
    result = await db.execute(query)
    tarefas = result.scalars().all()

    return [
        TarefaResponse(
            id=t.id, titulo=t.titulo, descricao=t.descricao,
            status=t.status, prioridade=t.prioridade, prazo=t.prazo,
            criador=t.criador, responsavel=t.responsavel,
            empresa_nome=t.empresa.nome if t.empresa else None,
            esta_atrasada=t.esta_atrasada,
            created_at=t.created_at, done_at=t.done_at,
        )
        for t in tarefas
    ]


@router.post("/", response_model=TarefaResponse, status_code=status.HTTP_201_CREATED)
async def criar_tarefa(
    dados: TarefaCreate,
    db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    """Cria nova tarefa e notifica o responsável."""
    tarefa = Tarefa(
        titulo=dados.titulo,
        descricao=dados.descricao,
        prioridade=dados.prioridade,
        prazo=dados.prazo,
        criado_por=current_user.id,
        atribuido_a=dados.atribuido_a,
        empresa_id=dados.empresa_id,
    )
    db.add(tarefa)
    await db.flush()

    # TODO: Disparar notificação push + in-app para o responsável
    logger.info("tarefa_criada", tarefa_id=str(tarefa.id), atribuido=str(dados.atribuido_a))

    return TarefaResponse(
        id=tarefa.id, titulo=tarefa.titulo, descricao=tarefa.descricao,
        status=tarefa.status, prioridade=tarefa.prioridade, prazo=tarefa.prazo,
        criador=tarefa.criador, responsavel=tarefa.responsavel,
        esta_atrasada=False, created_at=tarefa.created_at, done_at=None,
    )


@router.patch("/{tarefa_id}", response_model=TarefaResponse)
async def atualizar_tarefa(
    tarefa_id: UUID,
    dados: TarefaUpdate,
    db: DbSession,
    current_user=Depends(get_current_user),
):
    """
    Atualiza tarefa. Funcionário pode alterar apenas status (kanban drag).
    Gestor+ pode alterar qualquer campo.
    """
    result = await db.execute(select(Tarefa).where(Tarefa.id == tarefa_id))
    tarefa = result.scalar_one_or_none()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    # Funcionário só pode alterar status da própria tarefa
    if current_user.role == "funcionario":
        if tarefa.atribuido_a != current_user.id:
            raise HTTPException(status_code=403, detail="Sem permissão")
        if dados.model_dump(exclude_unset=True).keys() - {"status"}:
            raise HTTPException(status_code=403, detail="Funcionário pode alterar apenas o status")

    update_data = dados.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        setattr(tarefa, campo, valor)

    # Se marcou como done, registrar timestamp
    if dados.status == "done" and not tarefa.done_at:
        tarefa.done_at = datetime.now(timezone.utc)
    elif dados.status and dados.status != "done":
        tarefa.done_at = None

    await db.flush()
    return TarefaResponse(
        id=tarefa.id, titulo=tarefa.titulo, descricao=tarefa.descricao,
        status=tarefa.status, prioridade=tarefa.prioridade, prazo=tarefa.prazo,
        criador=tarefa.criador, responsavel=tarefa.responsavel,
        empresa_nome=tarefa.empresa.nome if tarefa.empresa else None,
        esta_atrasada=tarefa.esta_atrasada,
        created_at=tarefa.created_at, done_at=tarefa.done_at,
    )
