from sqlalchemy import Column, Integer, String

from ..db.base import Base


class Reply(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
