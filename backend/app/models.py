"""SQLAlchemy ORM models."""
from sqlalchemy import Column, Integer, String, DateTime, func

from app.database import Base


class URL(Base):
    """A single shortened URL record."""

    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)

    # The randomly generated short code, e.g. "aZ3xQ1".
    # Indexed + unique for fast, collision-free lookups on GET /{short_code}.
    short_code = Column(String(10), unique=True, index=True, nullable=False)

    # The original long URL the short code redirects to.
    # Unique + indexed so concurrent duplicate submissions can't create
    # two rows, and so the dedup lookup on every POST /shorten stays fast.
    original_url = Column(String, unique=True, index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
