# backend/app/core/security.py
# Módulo central de segurança do Portal TRK.
# Responsabilidades:
#   - JWT HS256: criação e verificação de access/refresh tokens
#   - Hashing de senhas com bcrypt (12 rounds)
#   - Criptografia AES-256-GCM para dados sensíveis em repouso
#   - Validação de força de senha
#   - Geração de tokens one-time para reset de senha

import base64
import hashlib
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings

# ════════════════════════════════════════════════════════════════
# JWT HS256
# ════════════════════════════════════════════════════════════════

ALGORITHM = "HS256"


def criar_access_token(dados: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Cria um access token JWT HS256 com expiração curta (padrão 60min)."""
    settings = get_settings()
    agora = datetime.now(timezone.utc)
    expira = agora + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    payload = {
        **dados,
        "exp": expira,
        "iat": agora,
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def criar_refresh_token(dados: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Cria um refresh token JWT HS256 com expiração longa (padrão 7 dias)."""
    settings = get_settings()
    agora = datetime.now(timezone.utc)
    expira = agora + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    payload = {
        **dados,
        "exp": expira,
        "iat": agora,
        "type": "refresh",
        "jti": secrets.token_urlsafe(32),  # ID único para revogação
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def verificar_token(token: str, tipo_esperado: str = "access") -> dict[str, Any]:
    """
    Verifica e decodifica um JWT. Valida expiração e tipo.
    Lança jwt.InvalidTokenError se inválido.
    """
    settings = get_settings()
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])

    if payload.get("type") != tipo_esperado:
        raise jwt.InvalidTokenError(f"Tipo de token inválido: esperado {tipo_esperado}")

    return payload


# ════════════════════════════════════════════════════════════════
# HASHING DE SENHAS (bcrypt 12 rounds)
# ════════════════════════════════════════════════════════════════

def hash_senha(senha: str) -> str:
    """Gera hash bcrypt com 12 rounds."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(senha.encode("utf-8"), salt).decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Verifica se a senha corresponde ao hash armazenado."""
    return bcrypt.checkpw(senha.encode("utf-8"), hash_armazenado.encode("utf-8"))


def hash_token(token: str) -> str:
    """Hash SHA-256 para armazenar refresh tokens no banco (não armazenar raw)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ════════════════════════════════════════════════════════════════
# VALIDAÇÃO DE SENHA FORTE
# ════════════════════════════════════════════════════════════════

SENHA_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,}$"
)


def validar_forca_senha(senha: str) -> tuple[bool, str]:
    """
    Valida se a senha atende aos requisitos:
    - Mínimo 8 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 número
    - Pelo menos 1 símbolo especial
    Retorna (válida, mensagem_erro).
    """
    if len(senha) < 8:
        return False, "Senha deve ter no mínimo 8 caracteres"
    if not re.search(r"[A-Z]", senha):
        return False, "Senha deve conter pelo menos 1 letra maiúscula"
    if not re.search(r"[a-z]", senha):
        return False, "Senha deve conter pelo menos 1 letra minúscula"
    if not re.search(r"\d", senha):
        return False, "Senha deve conter pelo menos 1 número"
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", senha):
        return False, "Senha deve conter pelo menos 1 símbolo especial"
    return True, ""


# ════════════════════════════════════════════════════════════════
# CRIPTOGRAFIA AES-256-GCM (dados sensíveis em repouso)
# ════════════════════════════════════════════════════════════════
# Formato armazenado: base64(IV_12bytes + ciphertext + tag_16bytes)


def criptografar_campo(valor: str) -> str:
    """
    Criptografa um valor string com AES-256-GCM.
    Retorna string base64 contendo IV + ciphertext + tag.
    Cada chamada gera um IV aleatório — mesmo valor produz resultado diferente.
    """
    settings = get_settings()
    chave = settings.encryption_key_bytes
    aesgcm = AESGCM(chave)
    iv = os.urandom(12)  # 96-bit nonce recomendado para GCM
    ciphertext = aesgcm.encrypt(iv, valor.encode("utf-8"), None)
    # ciphertext já inclui o authentication tag (16 bytes no final)
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def descriptografar_campo(valor_cifrado: str) -> str:
    """
    Descriptografa um valor criptografado com AES-256-GCM.
    Espera string base64 no formato IV(12) + ciphertext + tag(16).
    Lança exceção se o valor foi adulterado (GCM detecta).
    """
    settings = get_settings()
    chave = settings.encryption_key_bytes
    aesgcm = AESGCM(chave)
    dados = base64.b64decode(valor_cifrado)
    iv = dados[:12]
    ciphertext = dados[12:]
    return aesgcm.decrypt(iv, ciphertext, None).decode("utf-8")


# ════════════════════════════════════════════════════════════════
# TOKEN ONE-TIME (reset de senha)
# ════════════════════════════════════════════════════════════════

def gerar_token_reset() -> str:
    """Gera token URL-safe de 32 bytes para reset de senha."""
    return secrets.token_urlsafe(32)
