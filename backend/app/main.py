"""
URL Shortener API
==================

A minimal, production-style URL shortener built with FastAPI + PostgreSQL.

Endpoints
---------
POST /shorten          Accept a long URL, return a shortened URL.
GET  /{short_code}      Redirect to the original URL.
GET  /health            Basic health check.

Run with:  uvicorn app.main:app --reload
See README.md for full setup instructions.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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

# Allow the separate frontend folder (served from localhost:5500) to call
# this API from a browser. Restrict to your real frontend origin in prod.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
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


@app.get("/{short_code}", tags=["shortener"])
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    """Redirect a short code to its original long URL (404 if not found)."""
    db_url = crud.get_url_by_short_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=db_url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
