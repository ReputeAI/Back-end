from datetime import timedelta

import redis
from fastapi import HTTPException, status
from passlib.hash import argon2
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_token_hash,
    decode_token,
)
from ..models import RefreshToken, User


class AuthService:
    def __init__(self) -> None:
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)

    def register_user(self, db: Session, email: str, password: str) -> User:
        hashed = argon2.hash(password)
        user = User(email=email, hashed_password=hashed)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email).first()
        if not user or not argon2.verify(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user

    def create_tokens(self, db: Session, user: User) -> tuple[str, str]:
        access = create_access_token(str(user.id))
        refresh, jti = create_refresh_token(str(user.id))
        token_hash = hash_token(refresh)
        rt = RefreshToken(user_id=user.id, jti=jti, token_hash=token_hash)
        db.add(rt)
        db.commit()
        self.redis.setex(f"rt:{jti}", int(timedelta(days=7).total_seconds()), "active")
        return access, refresh

    def refresh(self, db: Session, refresh_token: str) -> tuple[str, str]:
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        if self.redis.get(f"revoked:{jti}"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
        stored = db.query(RefreshToken).filter_by(jti=jti).first()
        if not stored or not verify_token_hash(refresh_token, stored.token_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # rotate
        stored.revoked = True
        self.redis.set(f"revoked:{jti}", "1")
        access, refresh = self.create_tokens(db, db.get(User, stored.user_id))
        db.commit()
        return access, refresh

    def logout(self, db: Session, refresh_token: str) -> None:
        payload = decode_token(refresh_token)
        jti = payload.get("jti")
        self.redis.set(f"revoked:{jti}", "1")
        stored = db.query(RefreshToken).filter_by(jti=jti).first()
        if stored:
            stored.revoked = True
            db.commit()
