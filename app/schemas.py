"""Pydantic schemas — define the shape of API requests and responses."""
from datetime import datetime

from pydantic import BaseModel, HttpUrl, ConfigDict


class URLCreateRequest(BaseModel):
    """Body for POST /shorten."""

    # HttpUrl gives us automatic validation that the input is a well-formed
    # URL (has a scheme like http/https, a valid host, etc.) for free.
    original_url: HttpUrl


class URLResponse(BaseModel):
    """Response returned after successfully shortening a URL."""

    short_code: str
    short_url: str
    original_url: str
    created_at: datetime

    # Lets Pydantic build this schema directly from a SQLAlchemy model
    # instance (accessing attributes instead of requiring a dict).
    model_config = ConfigDict(from_attributes=True)


class URLStatsResponse(URLResponse):
    """Response for the optional stats endpoint — adds click count."""

    clicks: int
