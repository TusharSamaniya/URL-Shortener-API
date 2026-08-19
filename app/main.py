"""
URL Shortener API
==================

A minimal, production-style URL shortener built with FastAPI + PostgreSQL.

Endpoints
---------
POST /shorten          Accept a long URL, return a shortened URL.
GET  /{short_code}      Redirect to the original URL.
GET  /shorten/{code}/stats   (bonus) View click stats for a short code.
GET  /health            Basic health check.

Run with:  uvicorn app.main:app --reload
See README.md for full setup instructions.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.config import settings
from app.database import engine, get_db

# Create all tables on startup if they don't already exist.
# For a real production system you'd typically use Alembic migrations
# instead, but create_all() keeps this assignment simple to run.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="URL Shortener API",
    description="A basic URL shortener built with FastAPI and PostgreSQL.",
    version="1.0.0",
)


@app.get("/health", tags=["health"])
def health_check():
    """Simple liveness check — useful for monitoring/deployment."""
    return {"status": "ok"}


@app.post(
    "/shorten",
    response_model=schemas.URLResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["shortener"],
)
def shorten_url(payload: schemas.URLCreateRequest, db: Session = Depends(get_db)):
    """
    Accept a long URL and return a shortened version of it.

    - Validates that `original_url` is a well-formed URL (via Pydantic's
      HttpUrl type).
    - If the URL has already been shortened before, the same short code
      is returned instead of creating a duplicate entry.
    """
    db_url = crud.create_short_url(db, original_url=str(payload.original_url))

    return schemas.URLResponse(
        short_code=db_url.short_code,
        short_url=f"{settings.BASE_URL}/{db_url.short_code}",
        original_url=db_url.original_url,
        created_at=db_url.created_at,
    )


@app.get("/shorten/{short_code}/stats", response_model=schemas.URLStatsResponse, tags=["shortener"])
def get_stats(short_code: str, db: Session = Depends(get_db)):
    """(Bonus) Return metadata and click count for a given short code."""
    db_url = crud.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short code not found")

    return schemas.URLStatsResponse(
        short_code=db_url.short_code,
        short_url=f"{settings.BASE_URL}/{db_url.short_code}",
        original_url=db_url.original_url,
        created_at=db_url.created_at,
        clicks=db_url.clicks,
    )


@app.get("/{short_code}", tags=["shortener"])
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    """
    Redirect a short code to its original long URL.

    Returns a 404 if the short code doesn't exist, and increments the
    click counter on every successful redirect.
    """
    db_url = crud.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Record the visit, but never let a tracking failure break the redirect.
    try:
        crud.increment_clicks(db, db_url)
    except Exception:
        pass

    return RedirectResponse(url=db_url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
