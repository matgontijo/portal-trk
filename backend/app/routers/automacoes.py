# trk-universe/backend/app/routers/automacoes.py
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Automacao, User
from ..permissions import require_permission

router = APIRouter()
VER = require_permission("automacoes", "ver")
EDITAR = require_permission("automacoes", "editar")

GATILHOS = ["saldo_divergencia", "saldo_atualizado", "rotina_atrasada", "tarefa_criada", "card_movido"]
ACOES = ["notificar", "criar_tarefa", "whatsapp", "webhook"]


def _out(a: Automacao) -> dict:
    return {"id": a.id, "nome": a.nome, "gatilho": a.gatilho, "condicao": a.condicao,
            "acao": a.acao, "acao_config": a.acao_config, "ativa": a.ativa, "execucoes": a.execucoes}


@router.get("/meta")
def meta(_: User = Depends(VER)):
    return {"gatilhos": GATILHOS, "acoes": ACOES, "operadores": ["==", "!=", ">", ">=", "<", "<=", "contains"]}


@router.get("")
def listar(db: Session = Depends(get_db), _: User = Depends(VER)):
    return [_out(a) for a in db.execute(select(Automacao).order_by(Automacao.created_at.desc())).scalars().all()]


@router.post("", status_code=status.HTTP_201_CREATED)
def criar(payload: dict = Body(...), db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    a = Automacao(nome=payload.get("nome", "Automação"), gatilho=payload["gatilho"],
                  condicao=payload.get("condicao", {}), acao=payload["acao"],
                  acao_config=payload.get("acao_config", {}), ativa=payload.get("ativa", True))
    db.add(a)
    db.commit()
    db.refresh(a)
    return _out(a)


@router.put("/{aid}")
def atualizar(aid: str, payload: dict = Body(...), db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    a = db.get(Automacao, aid)
    if not a:
        raise HTTPException(404, "Não encontrada")
    for campo in ("nome", "gatilho", "condicao", "acao", "acao_config", "ativa"):
        if campo in payload:
            setattr(a, campo, payload[campo])
    db.commit()
    return _out(a)


@router.delete("/{aid}", status_code=status.HTTP_204_NO_CONTENT)
def remover(aid: str, db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    a = db.get(Automacao, aid)
    if a:
        db.delete(a)
        db.commit()
