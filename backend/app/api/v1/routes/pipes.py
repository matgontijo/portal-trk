# backend/app/api/v1/routes/pipes.py
# API do subsistema de Pipes (estilo Pipefy): pipes, fases, campos, cards e board.

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import DbSession, get_current_user, require_role
from app.db.models.pipe import (
    Pipe, PipeCampo, PipeCard, PipeCardHistorico, PipeFase,
)
from app.schemas.pipe import (
    BoardFase, BoardResponse, CampoCreate, CampoResponse, CardCreate,
    CardMove, CardResponse, CardUpdate, ComentarioCreate, FaseCreate,
    FaseResponse, HistoricoResponse, PipeCreate, PipeResponse, PipeUpdate,
)
from app.services.pipes import calcular_sla_status, fases_do_template

router = APIRouter()


# ─────────────────────────── helpers ───────────────────────────
def _card_to_response(card: PipeCard, sla_horas: int | None) -> CardResponse:
    return CardResponse(
        id=card.id, pipe_id=card.pipe_id, fase_id=card.fase_id, titulo=card.titulo,
        valores=card.valores or {}, ordem=card.ordem, concluido=card.concluido,
        valor_monetario=card.valor_monetario, prazo=card.prazo,
        fase_entrou_em=card.fase_entrou_em, atribuido_a=card.atribuido_a,
        empresa_id=card.empresa_id,
        responsavel_nome=card.responsavel.name if card.responsavel else None,
        empresa_nome=card.empresa.nome if card.empresa else None,
        sla_status=calcular_sla_status(sla_horas, card.fase_entrou_em),
        created_at=card.created_at,
    )


async def _get_pipe_ou_404(db, pipe_id: UUID) -> Pipe:
    pipe = await db.get(Pipe, pipe_id)
    if not pipe:
        raise HTTPException(404, "Pipe não encontrado")
    return pipe


async def _get_card_ou_404(db, card_id: UUID) -> PipeCard:
    card = await db.get(PipeCard, card_id)
    if not card:
        raise HTTPException(404, "Card não encontrado")
    return card


# ─────────────────────────── pipes ───────────────────────────
@router.get("/", response_model=list[PipeResponse])
async def listar_pipes(db: DbSession, current_user=Depends(get_current_user)):
    result = await db.execute(select(Pipe).where(Pipe.is_active == True).order_by(Pipe.created_at))  # noqa: E712
    return result.scalars().all()


@router.post("/", response_model=PipeResponse, status_code=status.HTTP_201_CREATED)
async def criar_pipe(
    payload: PipeCreate, db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    pipe = Pipe(
        nome=payload.nome, descricao=payload.descricao,
        cor=payload.cor, icone=payload.icone, created_by=current_user.id,
    )
    db.add(pipe)
    await db.flush()

    fases = [f.model_dump() for f in payload.fases] if payload.fases else fases_do_template(payload.usar_template)
    for i, f in enumerate(fases):
        db.add(PipeFase(
            pipe_id=pipe.id, nome=f["nome"], ordem=f.get("ordem", i),
            cor=f.get("cor", "#94a3b8"), is_final=f.get("is_final", False),
            sla_horas=f.get("sla_horas"),
        ))
    await db.commit()
    await db.refresh(pipe)
    return pipe


@router.get("/{pipe_id}", response_model=PipeResponse)
async def obter_pipe(pipe_id: UUID, db: DbSession, current_user=Depends(get_current_user)):
    return await _get_pipe_ou_404(db, pipe_id)


@router.put("/{pipe_id}", response_model=PipeResponse)
async def atualizar_pipe(
    pipe_id: UUID, payload: PipeUpdate, db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    pipe = await _get_pipe_ou_404(db, pipe_id)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(pipe, campo, valor)
    await db.commit()
    await db.refresh(pipe)
    return pipe


@router.delete("/{pipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_pipe(
    pipe_id: UUID, db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    pipe = await _get_pipe_ou_404(db, pipe_id)
    await db.delete(pipe)
    await db.commit()


# ─────────────────────────── fases ───────────────────────────
@router.post("/{pipe_id}/fases", response_model=FaseResponse, status_code=201)
async def criar_fase(
    pipe_id: UUID, payload: FaseCreate, db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    await _get_pipe_ou_404(db, pipe_id)
    fase = PipeFase(pipe_id=pipe_id, **payload.model_dump())
    db.add(fase)
    await db.commit()
    await db.refresh(fase)
    return fase


@router.put("/fases/{fase_id}", response_model=FaseResponse)
async def atualizar_fase(
    fase_id: UUID, payload: FaseCreate, db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    fase = await db.get(PipeFase, fase_id)
    if not fase:
        raise HTTPException(404, "Fase não encontrada")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(fase, campo, valor)
    await db.commit()
    await db.refresh(fase)
    return fase


@router.delete("/fases/{fase_id}", status_code=204)
async def deletar_fase(
    fase_id: UUID, db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    fase = await db.get(PipeFase, fase_id)
    if not fase:
        raise HTTPException(404, "Fase não encontrada")
    await db.delete(fase)
    await db.commit()


# ─────────────────────────── campos ───────────────────────────
@router.post("/{pipe_id}/campos", response_model=CampoResponse, status_code=201)
async def criar_campo(
    pipe_id: UUID, payload: CampoCreate, db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    await _get_pipe_ou_404(db, pipe_id)
    campo = PipeCampo(pipe_id=pipe_id, **payload.model_dump())
    db.add(campo)
    await db.commit()
    await db.refresh(campo)
    return campo


@router.delete("/campos/{campo_id}", status_code=204)
async def deletar_campo(
    campo_id: UUID, db: DbSession,
    current_user=Depends(require_role(["admin", "gestor"])),
):
    campo = await db.get(PipeCampo, campo_id)
    if not campo:
        raise HTTPException(404, "Campo não encontrado")
    await db.delete(campo)
    await db.commit()


# ─────────────────────────── board ───────────────────────────
@router.get("/{pipe_id}/board", response_model=BoardResponse)
async def board(pipe_id: UUID, db: DbSession, current_user=Depends(get_current_user)):
    """Retorna o pipe com fases e cards agrupados por fase (para o kanban)."""
    pipe = await _get_pipe_ou_404(db, pipe_id)
    sla_por_fase = {f.id: f.sla_horas for f in pipe.fases}

    result = await db.execute(
        select(PipeCard).where(PipeCard.pipe_id == pipe_id).order_by(PipeCard.ordem, PipeCard.created_at)
    )
    cards = result.scalars().all()

    por_fase: dict[UUID, list[CardResponse]] = {f.id: [] for f in pipe.fases}
    for card in cards:
        por_fase.setdefault(card.fase_id, []).append(
            _card_to_response(card, sla_por_fase.get(card.fase_id))
        )

    colunas = [BoardFase(fase=FaseResponse.model_validate(f), cards=por_fase.get(f.id, [])) for f in pipe.fases]
    return BoardResponse(pipe=PipeResponse.model_validate(pipe), colunas=colunas)


# ─────────────────────────── cards ───────────────────────────
@router.post("/{pipe_id}/cards", response_model=CardResponse, status_code=201)
async def criar_card(
    pipe_id: UUID, payload: CardCreate, db: DbSession,
    current_user=Depends(get_current_user),
):
    pipe = await _get_pipe_ou_404(db, pipe_id)
    if not pipe.fases:
        raise HTTPException(422, "O pipe não possui fases configuradas")

    fase_id = payload.fase_id or pipe.fases[0].id
    card = PipeCard(
        pipe_id=pipe_id, fase_id=fase_id, titulo=payload.titulo,
        valores=payload.valores or {}, valor_monetario=payload.valor_monetario,
        prazo=payload.prazo, atribuido_a=payload.atribuido_a,
        empresa_id=payload.empresa_id, criado_por=current_user.id,
        fase_entrou_em=datetime.now(timezone.utc),
    )
    db.add(card)
    await db.flush()
    db.add(PipeCardHistorico(card_id=card.id, tipo="criacao", para_fase_id=fase_id, user_id=current_user.id))
    await db.commit()
    await db.refresh(card)
    sla = next((f.sla_horas for f in pipe.fases if f.id == fase_id), None)
    return _card_to_response(card, sla)


@router.put("/cards/{card_id}", response_model=CardResponse)
async def atualizar_card(
    card_id: UUID, payload: CardUpdate, db: DbSession,
    current_user=Depends(get_current_user),
):
    card = await _get_card_ou_404(db, card_id)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(card, campo, valor)
    await db.commit()
    await db.refresh(card)
    fase = await db.get(PipeFase, card.fase_id)
    return _card_to_response(card, fase.sla_horas if fase else None)


@router.patch("/cards/{card_id}/mover", response_model=CardResponse)
async def mover_card(
    card_id: UUID, payload: CardMove, db: DbSession,
    current_user=Depends(get_current_user),
):
    """Move o card para outra fase, registra no histórico e zera o relógio de SLA."""
    card = await _get_card_ou_404(db, card_id)
    nova_fase = await db.get(PipeFase, payload.fase_id)
    if not nova_fase or nova_fase.pipe_id != card.pipe_id:
        raise HTTPException(422, "Fase inválida para este pipe")

    de_fase = card.fase_id
    card.fase_id = payload.fase_id
    card.fase_entrou_em = datetime.now(timezone.utc)
    if payload.ordem is not None:
        card.ordem = payload.ordem
    if nova_fase.is_final:
        card.concluido = True

    db.add(PipeCardHistorico(
        card_id=card.id, tipo="movimentacao",
        de_fase_id=de_fase, para_fase_id=payload.fase_id, user_id=current_user.id,
    ))
    # Notifica o responsável sobre a movimentação
    if card.atribuido_a and card.atribuido_a != current_user.id:
        from app.db.models.notificacao import Notificacao
        db.add(Notificacao(
            user_id=card.atribuido_a, tipo="sistema",
            titulo=f"Card movido: {card.titulo}",
            mensagem=f"'{card.titulo}' foi movido para {nova_fase.nome}.",
            link_acao=f"/pipes/{card.pipe_id}",
        ))
    await db.commit()
    await db.refresh(card)
    return _card_to_response(card, nova_fase.sla_horas)


@router.delete("/cards/{card_id}", status_code=204)
async def deletar_card(
    card_id: UUID, db: DbSession, current_user=Depends(get_current_user),
):
    card = await _get_card_ou_404(db, card_id)
    await db.delete(card)
    await db.commit()


@router.get("/cards/{card_id}/historico", response_model=list[HistoricoResponse])
async def historico_card(
    card_id: UUID, db: DbSession, current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(PipeCardHistorico)
        .where(PipeCardHistorico.card_id == card_id)
        .order_by(PipeCardHistorico.created_at.desc())
    )
    return result.scalars().all()


@router.post("/cards/{card_id}/comentar", response_model=HistoricoResponse, status_code=201)
async def comentar_card(
    card_id: UUID, payload: ComentarioCreate, db: DbSession,
    current_user=Depends(get_current_user),
):
    await _get_card_ou_404(db, card_id)
    h = PipeCardHistorico(card_id=card_id, tipo="comentario", texto=payload.texto, user_id=current_user.id)
    db.add(h)
    await db.commit()
    await db.refresh(h)
    return h
