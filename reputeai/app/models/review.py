from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    UniqueConstraint,
)

from ..db.base import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("org_id", "platform", "external_id", name="uix_org_platform_external"),
    )

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, index=True, nullable=False)
    platform = Column(String, index=True, nullable=False)
    external_id = Column(String, nullable=False)
    author = Column(String, nullable=True)
    rating = Column(Integer, nullable=True)
    text = Column(String, nullable=True)
    lang = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, nullable=True)
