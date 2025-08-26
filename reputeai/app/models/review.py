from sqlalchemy import Column, Integer, String

from ..db.base import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
