# trk-universe/backend/app/permissions.py
# Ecossistema de permissões do TRK OS — o coração do sistema.
#
# Conceitos:
#   - MÓDULO: uma "peça de Lego" do sistema (saldos, conciliação, RH, pipes...).
#   - AÇÃO: "ver" ou "editar".
#   - Permissão efetiva do usuário: {modulo: {ver: bool, editar: bool}}.
#   - cargo "diretor" tem acesso total (bypass). Demais seguem o mapa de permissões.
#
# O gestor/diretor edita a MATRIZ (módulo × usuário) — bloqueio de informação por
# setor (ex.: só Financeiro vê Conciliação e Contas Bancárias) é aplicado AQUI,
# no backend (a API recusa 403), além de esconder no frontend.

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .db import get_db
from .models import User
from .security import decodificar_token

# ─────────────────────────── Registro de módulos ───────────────────────────
# grupo: usado para agrupar no menu e na matriz. sensivel: dado financeiro restrito.
MODULOS: list[dict] = [
    {"key": "dashboard", "label": "Visão Geral", "icone": "LayoutDashboard", "grupo": "Geral", "descricao": "Painel inicial adaptado ao seu papel.", "sensivel": False},
    {"key": "rotinas", "label": "Rotinas", "icone": "CheckSquare", "grupo": "Trabalho", "descricao": "Checklists recorrentes do dia a dia.", "sensivel": False},
    {"key": "pipes", "label": "Pipes", "icone": "GitBranch", "grupo": "Trabalho", "descricao": "Processos em kanban com fases e SLA.", "sensivel": False},
    {"key": "tarefas", "label": "Tarefas", "icone": "KanbanSquare", "grupo": "Trabalho", "descricao": "Quadro de tarefas pessoais e de equipe.", "sensivel": False},
    {"key": "skills", "label": "Skills", "icone": "Sparkles", "grupo": "Trabalho", "descricao": "Capacidades prontas instaláveis.", "sensivel": False},
    {"key": "automacoes", "label": "Automações", "icone": "Zap", "grupo": "Trabalho", "descricao": "Regras gatilho → condição → ação.", "sensivel": False},
    {"key": "saldos", "label": "Saldos", "icone": "Wallet", "grupo": "Financeiro", "descricao": "Saldos bancários diários verificados.", "sensivel": True},
    {"key": "conciliacao", "label": "Conciliação", "icone": "ArrowRightLeft", "grupo": "Financeiro", "descricao": "Conciliação banco × ERP com IA.", "sensivel": True},
    {"key": "contas_bancarias", "label": "Contas Bancárias", "icone": "Landmark", "grupo": "Financeiro", "descricao": "Credenciais e contas das empresas.", "sensivel": True},
    {"key": "empresas", "label": "Empresas", "icone": "Building2", "grupo": "Financeiro", "descricao": "Diretório das empresas do grupo.", "sensivel": True},
    {"key": "rh", "label": "RH / Pessoas", "icone": "Users", "grupo": "Setores", "descricao": "Colaboradores, admissões e ponto.", "sensivel": False},
    {"key": "comercial", "label": "Comercial", "icone": "TrendingUp", "grupo": "Setores", "descricao": "Funil de vendas e clientes.", "sensivel": False},
    {"key": "relatorios", "label": "Relatórios", "icone": "FileBarChart", "grupo": "Gestão", "descricao": "Relatórios e indicadores.", "sensivel": False},
    {"key": "usuarios", "label": "Usuários", "icone": "UserCog", "grupo": "Administração", "descricao": "Gestão de pessoas e acessos.", "sensivel": False},
    {"key": "departamentos", "label": "Departamentos", "icone": "Network", "grupo": "Administração", "descricao": "Setores e matriz de permissões.", "sensivel": False},
    {"key": "configuracoes", "label": "Configurações", "icone": "Settings", "grupo": "Administração", "descricao": "Ajustes gerais do sistema.", "sensivel": False},
]

MODULOS_INDEX = {m["key"]: m for m in MODULOS}
ACOES = ("ver", "editar")


def permissoes_efetivas(user: User) -> dict:
    """Mapa final de permissões do usuário (diretor = acesso total)."""
    if user.cargo == "diretor":
        return {m["key"]: {"ver": True, "editar": True} for m in MODULOS}
    base = dict(user.permissoes or {})
    # Garante a estrutura para todos os módulos (default negado)
    return {m["key"]: {"ver": bool(base.get(m["key"], {}).get("ver")),
                       "editar": bool(base.get(m["key"], {}).get("editar"))} for m in MODULOS}


def pode(user: User, modulo: str, acao: str = "ver") -> bool:
    return bool(permissoes_efetivas(user).get(modulo, {}).get(acao))


def modulos_acessiveis(user: User) -> list[str]:
    ef = permissoes_efetivas(user)
    return [k for k, v in ef.items() if v.get("ver")]


# ─────────────────────────── Dependências FastAPI ───────────────────────────
def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token ausente")
    payload = decodificar_token(authorization.split(" ", 1)[1])
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado")
    user = db.get(User, payload.get("sub"))
    if not user or not user.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário inválido")
    return user


def require_permission(modulo: str, acao: str = "ver"):
    """Dependência que bloqueia o acesso a um módulo/ação."""
    def _dep(user: User = Depends(get_current_user)) -> User:
        if not pode(user, modulo, acao):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Seu setor não tem acesso a '{MODULOS_INDEX.get(modulo, {}).get('label', modulo)}'.",
            )
        return user
    return _dep


def require_cargo(*cargos: str):
    """Dependência que exige um cargo específico (ex.: gestor/diretor)."""
    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.cargo not in cargos:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Ação restrita à gestão.")
        return user
    return _dep
