from sqlalchemy import Column, Integer

from ..db.base import Base


class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    units = Column(Integer, default=0)
