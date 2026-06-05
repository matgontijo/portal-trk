# trk-universe/backend/app/security.py
# Auth sem dependências externas: PBKDF2 (senha) + JWT HS256 (stdlib).
# Decisão: zero libs de auth => menos superfície de build/CVE e roda em qualquer lugar.

import base64
import hashlib
import hmac
import json
import os
import time

from .config import config

_PBKDF2_ITER = 200_000


# ─────────────────────────── Senhas ───────────────────────────
def hash_senha(senha: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, _PBKDF2_ITER)
    return f"{salt.hex()}:{dk.hex()}"


def verificar_senha(senha: str, hashed: str) -> bool:
    try:
        salt_hex, dk_hex = hashed.split(":")
        dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(salt_hex), _PBKDF2_ITER)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False


# ─────────────────────────── JWT HS256 ───────────────────────────
def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def criar_token(payload: dict, exp_seconds: int | None = None) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    body = dict(payload)
    body["exp"] = int(time.time()) + (exp_seconds or config.TOKEN_EXP_SECONDS)
    seg = _b64(json.dumps(header).encode()) + "." + _b64(json.dumps(body).encode())
    sig = hmac.new(config.SECRET_KEY.encode(), seg.encode(), hashlib.sha256).digest()
    return seg + "." + _b64(sig)


def decodificar_token(token: str) -> dict | None:
    try:
        seg, sig = token.rsplit(".", 1)
        esperado = hmac.new(config.SECRET_KEY.encode(), seg.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64(esperado), sig):
            return None
        payload = json.loads(_b64d(seg.split(".")[1]))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None
