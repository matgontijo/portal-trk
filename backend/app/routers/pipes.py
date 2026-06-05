# trk-universe/backend/app/routers/pipes.py
import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Pipe, PipeCard, User
from ..permissions import require_permission

router = APIRouter()
VER = require_permission("pipes", "ver")
EDITAR = require_permission("pipes", "editar")

TEMPLATES = {
    "padrao": [{"nome": "A Fazer", "cor": "#94a3b8"}, {"nome": "Em Andamento", "cor": "#f59e0b"}, {"nome": "Concluído", "cor": "#10b981", "final": True}],
    "contas_pagar": [{"nome": "Recebido", "cor": "#94a3b8"}, {"nome": "Análise", "cor": "#f59e0b"}, {"nome": "Aprovado", "cor": "#475569"}, {"nome": "Pago", "cor": "#10b981", "final": True}],
    "onboarding": [{"nome": "Lead", "cor": "#94a3b8"}, {"nome": "Documentação", "cor": "#f59e0b"}, {"nome": "Configuração", "cor": "#475569"}, {"nome": "Ativo", "cor": "#10b981", "final": True}],
}


def _fases(template: str) -> list:
    base = TEMPLATES.get(template, TEMPLATES["padrao"])
    return [{"id": uuid.uuid4().hex, "nome": f["nome"], "cor": f["cor"], "ordem": i, "final": f.get("final", False)} for i, f in enumerate(base)]


@router.get("")
def listar(db: Session = Depends(get_db), _: User = Depends(VER)):
    return [{"id": p.id, "nome": p.nome, "cor": p.cor, "fases": p.fases} for p in db.execute(select(Pipe).order_by(Pipe.created_at)).scalars().all()]


@router.post("", status_code=status.HTTP_201_CREATED)
def criar(payload: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(EDITAR)):
    p = Pipe(nome=payload.get("nome", "Novo pipe"), cor=payload.get("cor", "#171717"),
             fases=_fases(payload.get("template", "padrao")), departamento_id=user.departamento_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "nome": p.nome, "cor": p.cor, "fases": p.fases}


@router.get("/{pid}/board")
def board(pid: str, db: Session = Depends(get_db), _: User = Depends(VER)):
    p = db.get(Pipe, pid)
    if not p:
        raise HTTPException(404, "Pipe não encontrado")
    cards = db.execute(select(PipeCard).where(PipeCard.pipe_id == pid).order_by(PipeCard.ordem)).scalars().all()
    colunas = []
    for f in sorted(p.fases, key=lambda x: x["ordem"]):
        cs = [{"id": c.id, "titulo": c.titulo, "fase_id": c.fase_id, "valor": c.valor} for c in cards if c.fase_id == f["id"]]
        colunas.append({"fase": f, "cards": cs})
    return {"pipe": {"id": p.id, "nome": p.nome, "cor": p.cor}, "colunas": colunas}


@router.post("/{pid}/cards", status_code=status.HTTP_201_CREATED)
def criar_card(pid: str, payload: dict = Body(...), db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    p = db.get(Pipe, pid)
    if not p or not p.fases:
        raise HTTPException(404, "Pipe sem fases")
    fase_id = payload.get("fase_id") or p.fases[0]["id"]
    c = PipeCard(pipe_id=pid, fase_id=fase_id, titulo=payload.get("titulo", "Novo card"), valor=payload.get("valor"))
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "titulo": c.titulo, "fase_id": c.fase_id, "valor": c.valor}


@router.patch("/cards/{cid}/mover")
def mover(cid: str, payload: dict = Body(...), db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    c = db.get(PipeCard, cid)
    if not c:
        raise HTTPException(404, "Card não encontrado")
    c.fase_id = payload["fase_id"]
    db.commit()
    return {"ok": True}


@router.delete("/cards/{cid}", status_code=status.HTTP_204_NO_CONTENT)
def remover_card(cid: str, db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    c = db.get(PipeCard, cid)
    if c:
        db.delete(c)
        db.commit()
