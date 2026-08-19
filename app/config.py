"""
Application configuration.

All settings are read from environment variables (with sensible local
defaults), so the same code works locally, in Docker, and in production
just by changing environment variables — no code changes required.
"""
import os

from dotenv import load_dotenv

# Load variables from a local .env file if present (Docker/CI set the
# environment variables directly instead).
load_dotenv()


class Settings:
    # PostgreSQL connection string.
    # Format: postgresql://<user>:<password>@<host>:<port>/<database>
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/url_shortener",
    )

    # Base URL used to build the full shortened link returned to clients.
    # e.g. http://localhost:8000  ->  http://localhost:8000/aZ3xQ1
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # Length of the randomly generated short code.
    SHORT_CODE_LENGTH: int = int(os.getenv("SHORT_CODE_LENGTH", "6"))


settings = Settings()
