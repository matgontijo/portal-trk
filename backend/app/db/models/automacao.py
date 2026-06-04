# backend/app/db/models/automacao.py
# Motor de automações do Portal TRK — o "customize cowork" interno.
#
# Uma Automação é uma regra: QUANDO <gatilho> [E <condições>] ENTÃO <ação>.
# Exemplos:
#   - QUANDO saldo diverge E |delta| > 1000  ENTÃO cria tarefa urgente
#   - QUANDO sync falha                       ENTÃO notifica gestor + WhatsApp
#   - QUANDO rotina não concluída até 18h     ENTÃO escala para o responsável
#
# As condições ficam em JSONB para permitir customização total pela UI
# (estilo Pipefy/Cowork) sem precisar de deploy.

import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

GATILHOS = (
    "saldo_divergencia",
    "saldo_atualizado",
    "saldo_falha",
    "rotina_concluida",
    "rotina_atrasada",
    "tarefa_criada",
    "agendado",
)

ACOES = (
    "notificar",
    "criar_tarefa",
    "whatsapp",
    "webhook",
)


class Automacao(Base, TimestampMixin):
    """Regra de automação configurável (gatilho → condição → ação)."""

    __tablename__ = "automacoes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    gatilho: Mapped[str] = mapped_column(
        Enum(*GATILHOS, name="automacao_gatilho"), nullable=False, index=True
    )
    # Condições: {"logica": "and"|"or", "regras": [{"campo","op","valor"}, ...]}
    condicao: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    acao: Mapped[str] = mapped_column(
        Enum(*ACOES, name="automacao_acao"), nullable=False
    )
    # Config da ação: depende do tipo (titulo, prioridade, mensagem, url, etc.)
    acao_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    ativa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prioridade: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Estatística: quantas vezes já disparou (observabilidade)
    execucoes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    criador = relationship("User", foreign_keys=[created_by], lazy="joined")

    def __repr__(self) -> str:
        return f"<Automacao {self.nome} gatilho={self.gatilho} ativa={self.ativa}>"
