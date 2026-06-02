# backend/app/schemas/user.py
# Schemas de usuário — criação, atualização e resposta.

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

from app.core.security import validar_forca_senha


class UserCreate(BaseModel):
    """Criação de novo usuário (gestor+ pode criar)."""
    name: str
    email: EmailStr
    password: str
    role: Literal["admin", "gestor", "funcionario"] = "funcionario"
    phone_whatsapp: str | None = None
    sector: str | None = None

    @field_validator("password")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        valida, mensagem = validar_forca_senha(v)
        if not valida:
            raise ValueError(mensagem)
        return v


class UserUpdate(BaseModel):
    """Atualização de usuário."""
    name: str | None = None
    email: EmailStr | None = None
    role: Literal["admin", "gestor", "funcionario"] | None = None
    is_active: bool | None = None
    phone_whatsapp: str | None = None
    avatar_url: str | None = None
    sector: str | None = None


class UserResponse(BaseModel):
    """Resposta de usuário (sem dados sensíveis)."""
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    phone_whatsapp: str | None
    avatar_url: str | None
    sector: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    """Resumo do usuário (para listas e referências)."""
    id: UUID
    name: str
    role: str
    avatar_url: str | None = None

    model_config = {"from_attributes": True}
