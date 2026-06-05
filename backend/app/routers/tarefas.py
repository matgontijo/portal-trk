# trk-universe/backend/app/routers/tarefas.py
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tarefa, User
from ..permissions import get_current_user, require_permission

router = APIRouter()
VER = require_permission("tarefas", "ver")
EDITAR = require_permission("tarefas", "editar")


def _out(t: Tarefa) -> dict:
    return {
        "id": t.id, "titulo": t.titulo, "descricao": t.descricao, "status": t.status,
        "prioridade": t.prioridade, "ordem": t.ordem, "atribuido_a": t.atribuido_a,
    }


@router.get("")
def listar(db: Session = Depends(get_db), _: User = Depends(VER)):
    rows = db.execute(select(Tarefa).order_by(Tarefa.ordem, Tarefa.created_at)).scalars().all()
    return [_out(t) for t in rows]


@router.post("", status_code=status.HTTP_201_CREATED)
def criar(payload: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(EDITAR)):
    t = Tarefa(
        titulo=payload.get("titulo", "Nova tarefa"), descricao=payload.get("descricao"),
        status=payload.get("status", "todo"), prioridade=payload.get("prioridade", "normal"),
        atribuido_a=payload.get("atribuido_a") or user.id, criado_por=user.id,
        departamento_id=user.departamento_id,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return _out(t)


@router.put("/{tid}")
def atualizar(tid: str, payload: dict = Body(...), db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    t = db.get(Tarefa, tid)
    if not t:
        raise HTTPException(404, "Tarefa não encontrada")
    for campo in ("titulo", "descricao", "status", "prioridade", "ordem", "atribuido_a"):
        if campo in payload:
            setattr(t, campo, payload[campo])
    db.commit()
    return _out(t)


@router.delete("/{tid}", status_code=status.HTTP_204_NO_CONTENT)
def remover(tid: str, db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    t = db.get(Tarefa, tid)
    if t:
        db.delete(t)
        db.commit()
