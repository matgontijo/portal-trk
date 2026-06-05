# trk-universe/backend/app/routers/saldos.py
# Módulo financeiro (restrito): saldos diários verificados (provider fake).

import hashlib
import random
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Empresa, Saldo
from ..permissions import require_permission

router = APIRouter()
VER = require_permission("saldos", "ver")
EDITAR = require_permission("saldos", "editar")


def _fake_saldo(cnpj: str, dia: str) -> tuple[float, float]:
    rnd = random.Random(int(hashlib.sha256(f"{cnpj}{dia}".encode()).hexdigest()[:12], 16))
    banco = round(rnd.uniform(45_000, 4_800_000), 2)
    omie = banco if rnd.random() > 0.17 else round(banco + rnd.choice([-1, 1]) * rnd.uniform(150, 12_000), 2)
    return banco, round(omie, 2)


@router.get("")
def listar(db: Session = Depends(get_db), _=Depends(VER)):
    rows = db.execute(select(Saldo)).scalars().all()
    ultimos: dict[str, Saldo] = {}
    for s in rows:
        if s.empresa_id not in ultimos or s.synced_at > ultimos[s.empresa_id].synced_at:
            ultimos[s.empresa_id] = s
    out = []
    for s in ultimos.values():
        out.append({
            "id": s.id, "empresa_id": s.empresa_id,
            "empresa_nome": s.empresa.nome if s.empresa else "",
            "saldo_banco": s.saldo_banco, "saldo_omie": s.saldo_omie, "delta": s.delta,
            "tem_divergencia": s.tem_divergencia, "synced_at": s.synced_at,
        })
    out.sort(key=lambda x: x["empresa_nome"])
    return out


@router.post("/sync")
def sincronizar(db: Session = Depends(get_db), _=Depends(EDITAR)):
    """Gera o snapshot de saldo do dia para todas as empresas (idempotente)."""
    hoje = date.today().isoformat()
    empresas = db.execute(select(Empresa).where(Empresa.ativo.is_(True))).scalars().all()
    n = 0
    for emp in empresas:
        banco, omie = _fake_saldo(emp.cnpj or emp.id, hoje)
        delta = round(banco - omie, 2)
        existente = db.execute(
            select(Saldo).where(Saldo.empresa_id == emp.id, Saldo.data_referencia == hoje)
        ).scalar_one_or_none()
        s = existente or Saldo(empresa_id=emp.id, data_referencia=hoje)
        s.saldo_banco, s.saldo_omie, s.delta = banco, omie, delta
        s.tem_divergencia = abs(delta) > 0.05
        s.synced_at = datetime.now(timezone.utc)
        if not existente:
            db.add(s)
        n += 1
    db.commit()
    return {"sincronizadas": n}
