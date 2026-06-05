# trk-universe/backend/app/routers/departamentos.py
# Setores da empresa + template de permissões de cada um.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Departamento, User
from ..permissions import require_permission
from ..schemas import DepartamentoIn, DepartamentoOut

router = APIRouter()

VER = require_permission("departamentos", "ver")
EDITAR = require_permission("departamentos", "editar")


def _out(db: Session, d: Departamento) -> DepartamentoOut:
    total = db.execute(select(func.count()).select_from(User).where(User.departamento_id == d.id)).scalar()
    return DepartamentoOut(
        id=d.id, nome=d.nome, cor=d.cor, icone=d.icone, descricao=d.descricao,
        permissoes_padrao=d.permissoes_padrao or {}, total_usuarios=total or 0,
    )


@router.get("", response_model=list[DepartamentoOut])
def listar(db: Session = Depends(get_db), _=Depends(VER)):
    deps = db.execute(select(Departamento).order_by(Departamento.nome)).scalars().all()
    return [_out(db, d) for d in deps]


@router.post("", response_model=DepartamentoOut, status_code=status.HTTP_201_CREATED)
def criar(dados: DepartamentoIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    d = Departamento(**dados.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return _out(db, d)


@router.put("/{dep_id}", response_model=DepartamentoOut)
def atualizar(dep_id: str, dados: DepartamentoIn, db: Session = Depends(get_db), _=Depends(EDITAR)):
    d = db.get(Departamento, dep_id)
    if not d:
        raise HTTPException(404, "Departamento não encontrado")
    for campo, valor in dados.model_dump().items():
        setattr(d, campo, valor)
    db.commit()
    db.refresh(d)
    return _out(db, d)


@router.delete("/{dep_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(dep_id: str, db: Session = Depends(get_db), _=Depends(EDITAR)):
    d = db.get(Departamento, dep_id)
    if not d:
        raise HTTPException(404, "Departamento não encontrado")
    db.delete(d)
    db.commit()
