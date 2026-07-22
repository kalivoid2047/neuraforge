"""Cryptographic primitives for auth (ADR-0007, SRS §9).

- Passwords: Argon2id via argon2-cffi defaults (RFC 9106 first recommendation).
- Access tokens: EdDSA (Ed25519) JWTs, ≤15 min.
- Refresh/email tokens: 256-bit urlsafe secrets, stored as SHA-256 hashes.
"""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from ..core.config import get_settings

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def new_opaque_token() -> tuple[str, str]:
    """Return (token, sha256_hex). Only the hash is ever stored."""
    token = secrets.token_urlsafe(48)
    return token, hashlib.sha256(token.encode()).hexdigest()


def hash_opaque(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ── Ed25519 key management ──────────────────────────────────────────────
def _load_or_create_key() -> Ed25519PrivateKey:
    path = Path(get_settings().jwt_key_file)
    if path.exists():
        return serialization.load_pem_private_key(path.read_bytes(), password=None)  # type: ignore[return-value]
    if not get_settings().is_dev:
        raise RuntimeError(f"JWT key missing at {path} (provision via LoadCredential)")
    key = Ed25519PrivateKey.generate()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    return key


_private_key: Ed25519PrivateKey | None = None


def _key() -> Ed25519PrivateKey:
    global _private_key
    if _private_key is None:
        _private_key = _load_or_create_key()
    return _private_key


def make_access_token(user_id: uuid.UUID, role: str, token_version: int) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "role": role,
        "ver": token_version,
        "jti": secrets.token_hex(8),
        "iat": now,
        "exp": now + timedelta(seconds=get_settings().access_token_ttl_s),
    }
    return jwt.encode(claims, _key(), algorithm="EdDSA")


def decode_access_token(token: str) -> dict:
    """Raises jwt.PyJWTError on any failure (signature, exp, malformed)."""
    return jwt.decode(token, _key().public_key(), algorithms=["EdDSA"])
