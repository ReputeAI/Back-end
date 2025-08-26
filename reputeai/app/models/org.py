from sqlalchemy import Column, Integer, String

from ..db.base import Base


class Org(Base):
    __tablename__ = "orgs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
