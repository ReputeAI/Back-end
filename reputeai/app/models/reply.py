from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from ..db.base import Base


class Reply(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, index=True, nullable=False)
    review_id = Column(Integer, index=True, nullable=False)
    text = Column(String, nullable=False)
    is_auto = Column(Boolean, default=False)
    status = Column(String, default="draft", nullable=False)
    platform_status = Column(String, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
