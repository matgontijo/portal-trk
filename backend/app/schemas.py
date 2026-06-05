# trk-universe/backend/app/schemas.py
# Schemas Pydantic do TRK OS.

from datetime import datetime

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    email: str
    senha: str


class DepartamentoOut(BaseModel):
    id: str
    nome: str
    cor: str
    icone: str
    descricao: str | None = None
    permissoes_padrao: dict = {}
    total_usuarios: int = 0

    model_config = {"from_attributes": True}


class DepartamentoIn(BaseModel):
    nome: str
    cor: str = "#171717"
    icone: str = "Building2"
    descricao: str | None = None
    permissoes_padrao: dict = {}


class UserOut(BaseModel):
    id: str
    nome: str
    email: str
    cargo: str
    departamento_id: str | None = None
    departamento_nome: str | None = None
    avatar_cor: str
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserIn(BaseModel):
    nome: str
    email: str
    senha: str = Field(min_length=4)
    cargo: str = "colaborador"
    departamento_id: str | None = None
    permissoes: dict | None = None  # se ausente, herda do departamento


class UserUpdate(BaseModel):
    nome: str | None = None
    cargo: str | None = None
    departamento_id: str | None = None
    permissoes: dict | None = None
    ativo: bool | None = None
    senha: str | None = None


class MeOut(BaseModel):
    usuario: UserOut
    permissoes: dict
    modulos_acessiveis: list[str]


class TokenOut(BaseModel):
    token: str
    usuario: UserOut
    permissoes: dict
    modulos_acessiveis: list[str]
