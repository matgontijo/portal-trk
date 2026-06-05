# trk-universe/backend/app/routers/rotinas.py
import uuid
from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Rotina, RotinaProgresso, User
from ..permissions import get_current_user, require_permission
from ..recorrencia import descrever, ocorre_em

router = APIRouter()
VER = require_permission("rotinas", "ver")
EDITAR = require_permission("rotinas", "editar")


def _out(r: Rotina) -> dict:
    return {
        "id": r.id, "nome": r.nome, "descricao": r.descricao, "categoria": r.categoria,
        "tipo_recorrencia": r.tipo_recorrencia, "recorrencia_config": r.recorrencia_config,
        "dias_semana": r.dias_semana, "blocos": r.blocos, "atribuidos": r.atribuidos,
        "ativa": r.ativa, "recorrencia_texto": descrever(r.tipo_recorrencia, r.recorrencia_config, r.dias_semana),
    }


@router.get("")
def listar(db: Session = Depends(get_db), _: User = Depends(VER)):
    rows = db.execute(select(Rotina).order_by(Rotina.nome)).scalars().all()
    return [_out(r) for r in rows]


@router.get("/hoje")
def hoje(db: Session = Depends(get_db), user: User = Depends(VER)):
    """Rotinas do usuário para hoje (filtradas por recorrência) + progresso."""
    hoje_d = date.today()
    rows = db.execute(select(Rotina).where(Rotina.ativa.is_(True))).scalars().all()
    minhas = [r for r in rows if user.id in (r.atribuidos or []) and ocorre_em(r.tipo_recorrencia, r.recorrencia_config, r.dias_semana, hoje_d)]
    prog = {p.bloco_id: p for p in db.execute(
        select(RotinaProgresso).where(RotinaProgresso.user_id == user.id, RotinaProgresso.data_ref == hoje_d.isoformat())
    ).scalars().all()}
    out = []
    for r in minhas:
        blocos = []
        feitos = 0
        for b in (r.blocos or []):
            p = prog.get(b["id"])
            done = bool(p and p.is_done)
            feitos += done
            blocos.append({**b, "is_done": done, "valor_texto": p.valor_texto if p else None})
        out.append({**_out(r), "blocos": blocos, "total": len(r.blocos or []), "feitos": feitos})
    return out


@router.put("/progresso")
def progresso(payload: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(VER)):
    bloco_id = payload["bloco_id"]
    hoje_d = date.today().isoformat()
    p = db.execute(select(RotinaProgresso).where(
        RotinaProgresso.bloco_id == bloco_id, RotinaProgresso.user_id == user.id, RotinaProgresso.data_ref == hoje_d
    )).scalar_one_or_none()
    if not p:
        p = RotinaProgresso(rotina_id=payload.get("rotina_id", ""), bloco_id=bloco_id, user_id=user.id, data_ref=hoje_d)
        db.add(p)
    if "is_done" in payload:
        p.is_done = payload["is_done"]
    if "valor_texto" in payload:
        p.valor_texto = payload["valor_texto"]
    db.commit()
    return {"ok": True}


@router.post("", status_code=status.HTTP_201_CREATED)
def criar(payload: dict = Body(...), db: Session = Depends(get_db), user: User = Depends(EDITAR)):
    blocos = [{**b, "id": b.get("id") or uuid.uuid4().hex} for b in payload.get("blocos", [])]
    r = Rotina(
        nome=payload.get("nome", "Nova rotina"), descricao=payload.get("descricao"),
        tipo_recorrencia=payload.get("tipo_recorrencia", "semanal"),
        recorrencia_config=payload.get("recorrencia_config", {}),
        dias_semana=payload.get("dias_semana", [1, 2, 3, 4, 5]),
        categoria=payload.get("categoria", "geral"), blocos=blocos,
        atribuidos=payload.get("atribuidos", [user.id]), departamento_id=user.departamento_id,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return _out(r)


@router.put("/{rid}")
def atualizar(rid: str, payload: dict = Body(...), db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    r = db.get(Rotina, rid)
    if not r:
        raise HTTPException(404, "Rotina não encontrada")
    for campo in ("nome", "descricao", "tipo_recorrencia", "recorrencia_config", "dias_semana", "categoria", "ativa", "blocos", "atribuidos"):
        if campo in payload:
            setattr(r, campo, payload[campo])
    db.commit()
    return _out(r)


@router.delete("/{rid}", status_code=status.HTTP_204_NO_CONTENT)
def remover(rid: str, db: Session = Depends(get_db), _: User = Depends(EDITAR)):
    r = db.get(Rotina, rid)
    if r:
        db.delete(r)
        db.commit()
