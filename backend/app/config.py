import os
from typing import List

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

    # Comma-separated list of allowed CORS origins.
    # e.g. "http://localhost:5500,https://yourfrontend.com"
    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw = os.getenv("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500")
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings()
