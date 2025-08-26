from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from ..db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    jti = Column(String, unique=True, index=True, nullable=False)
    token_hash = Column(String, nullable=False)
    revoked = Column(Boolean, default=False)
