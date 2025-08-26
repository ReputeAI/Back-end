from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

engine = create_engine(settings.db_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
