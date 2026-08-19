"""
Database access ("CRUD") helpers.

Kept separate from the route handlers in main.py so the API layer stays
thin and the persistence logic is easy to test/reuse in isolation.
"""
import secrets
import string

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models
from app.config import settings

# Characters used to build short codes: mixed-case letters + digits (base62).
# Avoids ambiguous-looking URLs and keeps codes short while still having a
# huge keyspace (62^6 ≈ 56 billion possible codes at the default length).
_ALPHABET = string.ascii_letters + string.digits


def _generate_short_code(length: int = settings.SHORT_CODE_LENGTH) -> str:
    """Generate a random short code using a cryptographically secure RNG."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


def get_url_by_short_code(db: Session, short_code: str) -> models.URL | None:
    return db.query(models.URL).filter(models.URL.short_code == short_code).first()


def get_url_by_original(db: Session, original_url: str) -> models.URL | None:
    """Look up an existing row for this URL, so we don't create duplicates."""
    return (
        db.query(models.URL)
        .filter(models.URL.original_url == original_url)
        .first()
    )


def create_short_url(db: Session, original_url: str) -> models.URL:
    """
    Create a new short URL record.

    If this exact URL has already been shortened before, the existing
    record is returned instead of creating a duplicate — this keeps the
    table clean and gives callers a stable short_code per unique URL.

    Safe under concurrency: the unique constraints on `original_url` and
    `short_code` turn any lost race into an IntegrityError, which we
    simply roll back and retry (re-checking for the winner's row).
    """
    for _ in range(5):
        existing = get_url_by_original(db, original_url)
        if existing:
            return existing

        db_url = models.URL(short_code=_generate_short_code(), original_url=original_url)
        db.add(db_url)
        try:
            db.commit()
        except IntegrityError:
            # Either our short code collided, or another request just
            # created this same URL — roll back and try again.
            db.rollback()
            continue

        db.refresh(db_url)
        return db_url

    raise RuntimeError("Could not generate a unique short code, try again.")


def increment_clicks(db: Session, db_url: models.URL) -> None:
    # Increment in SQL (not `db_url.clicks += 1`) so concurrent requests
    # can't lose updates to a read-modify-write race.
    db.execute(
        update(models.URL)
        .where(models.URL.id == db_url.id)
        .values(clicks=models.URL.clicks + 1)
    )
    db.commit()
