# trk-universe/backend/app/routers/empresas.py
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Empresa, User
from ..permissions import require_permission

router = APIRouter()
VER = require_permission("empresas", "ver")


@router.get("")
def listar(db: Session = Depends(get_db), _: User = Depends(VER)):
    rows = db.execute(select(Empresa).order_by(Empresa.nome)).scalars().all()
    return [{"id": e.id, "nome": e.nome, "cnpj": e.cnpj, "banco": e.banco, "grupo": e.grupo, "ativo": e.ativo} for e in rows]
