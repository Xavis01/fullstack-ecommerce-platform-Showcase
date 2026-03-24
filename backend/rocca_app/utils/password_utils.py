"""
password_utils.py — Utilitários de criptografia de senha com bcrypt.

Estratégia de migração:
  - Novas senhas são sempre hasheadas com bcrypt.
  - No login, tenta verificar com bcrypt. Se falhar, tenta werkzeug (legado).
  - Se a senha for válida via werkzeug, re-hasheia com bcrypt e salva.
  - Após todos os usuários fazerem login uma vez, o legado werkzeug some naturalmente.
"""

import bcrypt
from werkzeug.security import check_password_hash as werkzeug_check


def hash_password(plain_password: str) -> str:
    """Gera um hash bcrypt a partir de uma senha plaintext."""
    password_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verifica se a senha bate com o hash armazenado.
    Suporta tanto bcrypt (novo) quanto werkzeug/pbkdf2 (legado).
    """
    if not plain_password or not stored_hash:
        return False

    # Bcrypt hashes sempre começam com $2b$ ou $2a$
    if stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$"):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), stored_hash.encode("utf-8"))
        except Exception:
            return False

    # Fallback: hash legado do werkzeug (pbkdf2:sha256:...)
    try:
        return werkzeug_check(stored_hash, plain_password)
    except Exception:
        return False


def needs_rehash(stored_hash: str) -> bool:
    """Retorna True se o hash ainda não é bcrypt (precisa ser atualizado)."""
    return not (stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$"))
