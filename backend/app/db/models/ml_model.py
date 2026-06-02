# backend/app/db/models/ml_model.py
# Model de versionamento de modelos ML do Portal TRK.
# Cada treinamento gera uma nova versão com métricas (precision, recall, F1).
# Apenas um modelo pode estar ativo (is_active=True) por vez.
# Admin pode fazer rollback para versão anterior.

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MLModelVersion(Base):
    __tablename__ = "ml_model_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    treinado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    precision_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    recall_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    f1_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    n_amostras_treino: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    n_amostras_validacao: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    arquivo_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    threshold_auto: Mapped[float] = mapped_column(
        Numeric(5, 4), nullable=False, default=0.90
    )
    treinado_por: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Relacionamentos ───
    usuario = relationship("User", lazy="joined")

    def __repr__(self) -> str:
        return f"<MLModelVersion f1={self.f1_score} ativa={self.is_active}>"
