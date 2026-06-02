# backend/app/schemas/auth.py
# Schemas de autenticação — login, tokens, registro, reset de senha.

from pydantic import BaseModel, EmailStr, field_validator

from app.core.security import validar_forca_senha


class LoginRequest(BaseModel):
    """Requisição de login com e-mail e senha."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Resposta com access token (refresh vai via cookie httpOnly)."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos


class RefreshRequest(BaseModel):
    """Requisição de refresh (token vem do cookie, não do body)."""
    pass


class ForgotPasswordRequest(BaseModel):
    """Requisição de reset de senha — envia token por e-mail."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Requisição para definir nova senha com token de reset."""
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        valida, mensagem = validar_forca_senha(v)
        if not valida:
            raise ValueError(mensagem)
        return v


class ChangePasswordRequest(BaseModel):
    """Requisição para alterar senha (logado)."""
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        valida, mensagem = validar_forca_senha(v)
        if not valida:
            raise ValueError(mensagem)
        return v
