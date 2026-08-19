from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# `pool_pre_ping` checks that a pooled connection is still alive before
# handing it out — avoids errors from stale connections after idle periods.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a DB session for a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
