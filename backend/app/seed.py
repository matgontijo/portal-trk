# trk-universe/backend/app/seed.py
# Popula o TRK OS com departamentos, matriz de permissões por setor, usuários
# demo e empresas — tudo pronto para demonstrar o ecossistema.

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Departamento, Empresa, User
from .permissions import MODULOS
from .security import hash_senha


def _perm(full: list[str] = (), ver: list[str] = ()) -> dict:
    """Monta um mapa de permissões: `full` = ver+editar, `ver` = só leitura."""
    mapa = {}
    for k in full:
        mapa[k] = {"ver": True, "editar": True}
    for k in ver:
        mapa.setdefault(k, {"ver": True, "editar": False})
    return mapa


# Templates de permissão por setor (bloqueio de informação por departamento)
TODOS = [m["key"] for m in MODULOS]
TEMPLATES = {
    "Diretoria": {
        "cor": "#171717", "icone": "Crown",
        "desc": "Visão consolidada de toda a empresa. Define setores e permissões.",
        "perm": _perm(full=TODOS),
    },
    "Financeiro": {
        "cor": "#10b981", "icone": "Wallet",
        "desc": "Conciliação, saldos e contas bancárias do grupo.",
        "perm": _perm(
            full=["dashboard", "saldos", "conciliacao", "contas_bancarias", "empresas",
                  "rotinas", "pipes", "tarefas", "skills", "automacoes"],
            ver=["relatorios"],
        ),
    },
    "RH / Pessoas": {
        "cor": "#f59e0b", "icone": "Users",
        "desc": "Gestão de pessoas, admissões e ponto. Sem acesso financeiro.",
        "perm": _perm(full=["dashboard", "rh", "rotinas", "pipes", "tarefas"], ver=["relatorios"]),
    },
    "Comercial": {
        "cor": "#3f3f46", "icone": "TrendingUp",
        "desc": "Funil de vendas, clientes e propostas.",
        "perm": _perm(full=["dashboard", "comercial", "pipes", "tarefas", "rotinas"]),
    },
    "Operações": {
        "cor": "#475569", "icone": "Workflow",
        "desc": "Execução de processos, rotinas e tarefas operacionais.",
        "perm": _perm(full=["dashboard", "rotinas", "pipes", "tarefas"], ver=["relatorios"]),
    },
}

# Usuários demo: (nome, email, cargo, departamento)
USUARIOS_DEMO = [
    ("Diretor TRK", "diretor@trk.com", "diretor", "Diretoria"),
    ("Gestor Financeiro", "financeiro@trk.com", "gestor", "Financeiro"),
    ("Analista Financeiro", "analista@trk.com", "colaborador", "Financeiro"),
    ("Gestora de RH", "rh@trk.com", "gestor", "RH / Pessoas"),
    ("Vendedor", "comercial@trk.com", "colaborador", "Comercial"),
    ("Coord. Operações", "operacoes@trk.com", "gestor", "Operações"),
]

SENHA_PADRAO = "Trk@123"


def seed(db: Session) -> None:
    if db.execute(select(User).limit(1)).first():
        return  # já populado

    deps: dict[str, Departamento] = {}
    for nome, t in TEMPLATES.items():
        d = Departamento(
            nome=nome, cor=t["cor"], icone=t["icone"],
            descricao=t["desc"], permissoes_padrao=t["perm"],
        )
        db.add(d)
        deps[nome] = d
    db.flush()

    for nome, email, cargo, dep_nome in USUARIOS_DEMO:
        dep = deps[dep_nome]
        db.add(User(
            nome=nome, email=email, senha_hash=hash_senha(SENHA_PADRAO),
            cargo=cargo, departamento_id=dep.id,
            permissoes=dict(dep.permissoes_padrao), avatar_cor=dep.cor,
        ))

    for i in range(1, 7):
        db.add(Empresa(nome=f"TRK Empreendimento {i:02d}", cnpj=f"1234567800{i:04d}",
                       banco="fake", grupo="trk" if i <= 3 else "bpo"))

    db.commit()
