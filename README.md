# URL Shortener

A URL shortener with a **FastAPI + PostgreSQL** backend and a simple web UI.

Users submit a long URL and receive a short code that redirects back to the
original URL.

---

## Project Structure

```
url-shortener/
├── backend/                 # FastAPI + PostgreSQL API
│   ├── app/
│   │   ├── main.py          # FastAPI app, routes & CORS
│   │   ├── models.py        # SQLAlchemy ORM model (the `urls` table)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── crud.py          # Database access logic (create/read/update)
│   │   ├── database.py      # SQLAlchemy engine/session setup
│   │   └── config.py        # Environment-based settings (+ .env loading)
│   ├── Dockerfile           # Builds the API image
│   ├── docker-compose.yml   # Runs PostgreSQL + the API together
│   ├── requirements.txt
│   ├── .env.example
│   └── test_api.py          # Automated tests (pytest)
├── frontend/                # Web UI (plain HTML/CSS/JS, no build step)
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── Dockerfile           # Serves the UI with nginx
├── README.md
└── .gitignore
```

The backend is split into layers (routes → CRUD → models) rather than one big
file, keeping each piece easy to read, test, and extend. The frontend is a
single self-contained page that talks to the API over HTTP.

---

## API Endpoints

- `POST /shorten` — submit a long URL, get back a short code + short URL
- `GET /{short_code}` — redirects (HTTP 307) to the original long URL
- `GET /health` — health check
- Interactive docs (Swagger UI) at `/docs`

The API accepts requests from the frontend origin (CORS is enabled for
`http://localhost:5500`). Duplicate URLs return the **same** short code, and
malformed URLs are rejected with a `422`.

---

## How to Run

### Option A — Docker Compose (recommended, runs everything)

One command builds and starts **PostgreSQL + API + frontend**:

```bash
cd backend
docker-compose up --build
```

- API: **http://localhost:8000** — docs at **http://localhost:8000/docs**
- Frontend UI: **http://localhost:5500**

### Option B — Run locally

Prerequisites: Python 3.11+, a running PostgreSQL instance.

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # adjust DATABASE_URL if needed
uvicorn app.main:app --reload
```

Then serve the frontend with any static server (no install step):

```bash
cd frontend
python -m http.server 5500
```

Open **http://localhost:5500** in a browser. The page reads the API base URL
from `API_BASE_URL` in `app.js` (defaults to `http://localhost:8000`), so make
sure the backend is running first.

---

## Example Usage

**Shorten a URL:**

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.example.com/a/very/long/path?query=123"}'
```

```json
{
  "short_code": "aZ3xQ1",
  "short_url": "http://localhost:8000/aZ3xQ1",
  "original_url": "https://www.example.com/a/very/long/path?query=123",
  "created_at": "2026-08-19T10:15:00Z"
}
```

**Use the short URL** (redirects to the original):

```bash
curl -L http://localhost:8000/aZ3xQ1
```

---

## Running Tests

```bash
cd backend
pip install pytest httpx
pytest test_api.py -v
```

The tests use a local SQLite file in place of PostgreSQL purely so they run
instantly with zero external setup — the application code is identical either
way, since SQLAlchemy abstracts the database engine. 6 tests cover: health
check, shortening, duplicate-URL handling, invalid-URL rejection, redirect
behavior, and 404 handling.

---

## Design Decisions & Trade-offs

- **Random short codes vs. incrementing/hash-based IDs:** random codes (via
  Python's `secrets` module, which is cryptographically secure) avoid leaking
  information like "how many URLs have been shortened" and don't require a
  separate ID-to-base62 encoding step. The trade-off is a very small chance of
  collision, handled with a retry loop.
- **Deduplication on `original_url`:** shortening the same URL twice returns
  the same code rather than creating a new row each time. The column is unique
  + indexed so this stays correct and fast under concurrent requests.
- **307 redirect (not 301):** a temporary redirect so browsers won't cache the
  redirect permanently if the underlying URL is ever updated.
- **`create_all()` instead of migrations:** for this scope, tables are created
  automatically on startup. A production system would use Alembic for versioned
  schema migrations.

## Possible Future Improvements

- Rate limiting to prevent abuse
- Custom/user-chosen short codes
- Link expiration dates
- User accounts & authentication so people can manage their own links
- Alembic migrations instead of `create_all()`