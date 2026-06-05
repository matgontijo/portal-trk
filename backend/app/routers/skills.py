# trk-universe/backend/app/routers/skills.py
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Automacao, Pipe, Rotina, User
from ..permissions import require_permission
from .pipes import _fases

router = APIRouter()
VER = require_permission("skills", "ver")
EDITAR = require_permission("skills", "editar")

SKILLS = [
    {"id": "fechamento-diario", "nome": "Fechamento diário de caixa", "categoria": "Financeiro", "icone": "Wallet", "tipo": "rotina",
     "descricao": "Checklist diário de conferência e conciliação.",
     "payload": {"nome": "Fechamento diário de caixa", "tipo_recorrencia": "diaria", "recorrencia_config": {"apenas_dias_uteis": True}, "categoria": "banco",
                 "blocos": [{"tipo": "checkbox", "label": "Conferir saldos"}, {"tipo": "checkbox", "label": "Conciliar lançamentos"}, {"tipo": "text_long", "label": "Pendências"}]}},
    {"id": "conciliacao-matinal", "nome": "Conciliação matinal", "categoria": "Financeiro", "icone": "Sunrise", "tipo": "rotina",
     "descricao": "Toda manhã revisar e aprovar conciliações.",
     "payload": {"nome": "Conciliação matinal", "tipo_recorrencia": "semanal", "dias_semana": [1, 2, 3, 4, 5], "categoria": "omie",
                 "blocos": [{"tipo": "checkbox", "label": "Revisar sugestões da IA"}, {"tipo": "checkbox", "label": "Aprovar matches"}]}},
    {"id": "alerta-divergencia", "nome": "Alerta de divergência alta", "categoria": "Financeiro", "icone": "AlertTriangle", "tipo": "automacao",
     "descricao": "Saldo divergir > R$1.000 → cria tarefa urgente.",
     "payload": {"nome": "Alerta de divergência alta", "gatilho": "saldo_divergencia", "condicao": {"regras": [{"campo": "delta_abs", "op": ">", "valor": 1000}]}, "acao": "criar_tarefa", "acao_config": {"titulo": "Conciliar divergência", "prioridade": "urgente"}}},
    {"id": "pipe-contas-pagar", "nome": "Pipe: Contas a Pagar", "categoria": "Pipes", "icone": "Receipt", "tipo": "pipe",
     "descricao": "Recebido → Análise → Aprovado → Pago.", "payload": {"nome": "Contas a Pagar", "template": "contas_pagar", "cor": "#10b981"}},
    {"id": "pipe-onboarding", "nome": "Pipe: Onboarding", "categoria": "Pipes", "icone": "UserPlus", "tipo": "pipe",
     "descricao": "Lead → Documentação → Configuração → Ativo.", "payload": {"nome": "Onboarding", "template": "onboarding", "cor": "#475569"}},
]
INDEX = {s["id"]: s for s in SKILLS}


@router.get("")
def listar(_: User = Depends(VER)):
    return [{k: s[k] for k in ("id", "nome", "descricao", "categoria", "icone", "tipo")} for s in SKILLS]


@router.post("/{sid}/instalar", status_code=status.HTTP_201_CREATED)
def instalar(sid: str, db: Session = Depends(get_db), user: User = Depends(EDITAR)):
    s = INDEX.get(sid)
    if not s:
        raise HTTPException(404, "Skill não encontrada")
    p, tipo = s["payload"], s["tipo"]
    if tipo == "rotina":
        blocos = [{**b, "id": uuid.uuid4().hex} for b in p.get("blocos", [])]
        db.add(Rotina(nome=p["nome"], tipo_recorrencia=p.get("tipo_recorrencia", "semanal"),
                      recorrencia_config=p.get("recorrencia_config", {}), dias_semana=p.get("dias_semana", []),
                      categoria=p.get("categoria", "geral"), blocos=blocos, atribuidos=[user.id], departamento_id=user.departamento_id))
    elif tipo == "automacao":
        db.add(Automacao(nome=p["nome"], gatilho=p["gatilho"], condicao=p.get("condicao", {}), acao=p["acao"], acao_config=p.get("acao_config", {})))
    elif tipo == "pipe":
        db.add(Pipe(nome=p["nome"], cor=p.get("cor", "#171717"), fases=_fases(p.get("template", "padrao")), departamento_id=user.departamento_id))
    db.commit()
    return {"status": "instalada", "nome": s["nome"], "tipo": tipo}
