# backend/app/db/models/__init__.py
# Re-exporta todos os models para facilitar importação.
# Importante: todos os models devem ser importados aqui para que
# o Alembic e o Base.metadata consigam detectar todas as tabelas.

from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.db.models.empresa import Empresa
from app.db.models.user_empresa import UserEmpresaAssignment
from app.db.models.rotina import Rotina, RotinaBloco, RotinaAtribuicao
from app.db.models.rotina_progresso import RotinaProgresso
from app.db.models.tarefa import Tarefa
from app.db.models.saldo import Saldo
from app.db.models.lancamento import LancamentoBanco, LancamentoOmie
from app.db.models.conciliacao import Conciliacao
from app.db.models.ml_model import MLModelVersion
from app.db.models.sync_config import SyncConfig
from app.db.models.notificacao import Notificacao
from app.db.models.push_subscription import PushSubscription
from app.db.models.audit_log import AuditLog
from app.db.models.automacao import Automacao

__all__ = [
    "User",
    "RefreshToken",
    "Empresa",
    "UserEmpresaAssignment",
    "Rotina",
    "RotinaBloco",
    "RotinaAtribuicao",
    "RotinaProgresso",
    "Tarefa",
    "Saldo",
    "LancamentoBanco",
    "LancamentoOmie",
    "Conciliacao",
    "MLModelVersion",
    "SyncConfig",
    "Notificacao",
    "PushSubscription",
    "AuditLog",
    "Automacao",
]
