from datetime import datetime, timedelta
from uuid import uuid4
from typing import Tuple

from jose import jwt
from passlib.hash import argon2

from .config import settings


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.jwt_private_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, jti: str | None = None) -> Tuple[str, str]:
    if jti is None:
        jti = str(uuid4())
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {"sub": subject, "exp": expire, "jti": jti, "type": "refresh"}
    token = jwt.encode(to_encode, settings.jwt_private_key, algorithm=settings.jwt_algorithm)
    return token, jti


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_public_key, algorithms=[settings.jwt_algorithm])


def hash_token(token: str) -> str:
    return argon2.hash(token)


def verify_token_hash(token: str, token_hash: str) -> bool:
    return argon2.verify(token, token_hash)
