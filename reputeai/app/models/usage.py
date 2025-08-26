from sqlalchemy import Column, Integer, String

from ..db.base import Base


class Usage(Base):
    __tablename__ = "usage"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, index=True, nullable=False)
    month = Column(String, index=True, nullable=False)
    units = Column(Integer, default=0)
