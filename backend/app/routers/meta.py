# trk-universe/backend/app/routers/meta.py
# Metadados do sistema: registro de módulos e KPIs do dashboard.

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Departamento, Empresa, User
from ..permissions import MODULOS, get_current_user, modulos_acessiveis

router = APIRouter()


@router.get("/modulos")
def listar_modulos(user: User = Depends(get_current_user)):
    """Registro de módulos + quais o usuário pode ver (para montar o menu)."""
    acessiveis = set(modulos_acessiveis(user))
    return {"modulos": MODULOS, "acessiveis": list(acessiveis)}


@router.get("/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """KPIs adaptados — quem não vê financeiro, não recebe dados financeiros."""
    acessiveis = set(modulos_acessiveis(user))
    data: dict = {
        "usuario": user.nome,
        "cargo": user.cargo,
        "departamento": user.departamento.nome if user.departamento else None,
        "total_usuarios": db.execute(select(func.count()).select_from(User)).scalar(),
        "total_departamentos": db.execute(select(func.count()).select_from(Departamento)).scalar(),
    }
    if "saldos" in acessiveis:
        from ..models import Saldo
        total = db.execute(select(func.coalesce(func.sum(Saldo.saldo_banco), 0))).scalar() or 0
        diverg = db.execute(select(func.count()).select_from(Saldo).where(Saldo.tem_divergencia.is_(True))).scalar()
        data["financeiro"] = {
            "total_em_caixa": float(total),
            "empresas": db.execute(select(func.count()).select_from(Empresa)).scalar(),
            "divergencias": diverg,
        }
    return data
