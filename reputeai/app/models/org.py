from sqlalchemy import Column, Integer, String, JSON

from ..db.base import Base


class Org(Base):
    __tablename__ = "orgs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    plan = Column(String, default="FREE", nullable=False)
    stripe_customer_id = Column(String, index=True, nullable=True)
    settings = Column(JSON, default=dict)
