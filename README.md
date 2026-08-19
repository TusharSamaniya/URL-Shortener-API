# URL Shortener API

A URL shortener REST API built with **FastAPI** and **PostgreSQL**. Users can
submit a long URL and receive a short code that redirects back to the
original URL.

---

## Features

- `POST /shorten` — submit a long URL, get back a short code + short URL
- `GET /{short_code}` — redirects (HTTP 307) to the original long URL
- `GET /shorten/{short_code}/stats` — bonus endpoint returning click count and metadata
- `GET /health` — basic health check
- Duplicate URLs return the **same** short code instead of creating redundant rows
- Input validation (rejects malformed URLs) with clear error responses
- Auto-generated interactive API docs (Swagger UI) at `/docs`
- Fully containerized with Docker Compose (API + PostgreSQL, one command to run)
- Automated tests covering the core behavior

---

## Project Structure

```
url-shortener/
├── app/
│   ├── main.py        # FastAPI app & route handlers
│   ├── models.py       # SQLAlchemy ORM model (the `urls` table)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── crud.py           # Database access logic (create/read/update)
│   ├── database.py        # SQLAlchemy engine/session setup
│   └── config.py            # Environment-based settings
├── test_api.py       # Automated tests (pytest)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml   # Runs Postgres + the API together
├── .env.example
└── README.md
```

The code is split into layers (routes → CRUD → models) rather than one big
file, which keeps each piece easy to read, test, and extend.

---

## How It Works

1. **`POST /shorten`** receives `{ "original_url": "<url>" }`.
   - Pydantic's `HttpUrl` type validates it's a real, well-formed URL.
   - The app checks if this exact URL was already shortened — if so, it
     returns the existing short code (avoids duplicate rows).
   - Otherwise, it generates a random 6-character code (mixed-case letters +
     digits — about 56 billion possible combinations) and checks it doesn't
     already exist in the database, retrying on the rare collision.
   - The new record is saved and the short URL is returned.

2. **`GET /{short_code}`** looks up the code in PostgreSQL. If found, it
   increments a click counter and issues an HTTP 307 redirect to the
   original URL. If not found, it returns a 404.

3. **`GET /shorten/{short_code}/stats`** (bonus) returns the original URL,
   creation time, and click count — useful for verifying the redirect/click
   tracking works, and a small demonstration of API design beyond the bare
   minimum spec.

---

## How to Run

### Option A — Docker Compose (recommended, one command)

This spins up PostgreSQL and the API together, with no local Python or
Postgres install needed.

```bash
docker-compose up --build
```

The API will be available at **http://localhost:8000**, with interactive
docs at **http://localhost:8000/docs**.

### Option B — Run locally

**Prerequisites:** Python 3.11+, a running PostgreSQL instance.

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# edit .env if your Postgres credentials/host differ from the defaults

# 4. Make sure PostgreSQL is running and the database in .env exists, e.g.:
#    createdb url_shortener

# 5. Run the API (tables are created automatically on startup)
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**.

---

## Example Usage

**Shorten a URL:**

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.example.com/a/very/long/path?query=123"}'
```

Response:

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

**Check stats:**

```bash
curl http://localhost:8000/shorten/aZ3xQ1/stats
```

You can also try all of this interactively via the Swagger UI at
`/docs` once the server is running.

---

## Running Tests

```bash
pip install pytest httpx
pytest test_api.py -v
```

The tests use a local SQLite file in place of PostgreSQL purely so they run
instantly with no external database to set up — the application code itself
is identical either way, since SQLAlchemy abstracts the database engine.
7 tests cover: health check, shortening, duplicate-URL handling, invalid-URL
rejection, redirect behavior, 404 handling, and click tracking.

---

## Design Decisions & Trade-offs

- **Random short codes vs. incrementing/hash-based IDs:** random codes
  (via Python's `secrets` module, which is cryptographically secure) avoid
  leaking information like "how many URLs have been shortened" and don't
  require a separate ID-to-base62 encoding step. The trade-off is a very
  small chance of collision, handled with a retry loop.
- **Deduplication on `original_url`:** shortening the same URL twice
  returns the same code rather than creating a new row each time. This
  keeps the table smaller and gives users a stable link per URL, at the
  cost of one extra lookup query per request.
- **307 redirect (not 301):** a temporary redirect was chosen so that if
  the underlying original URL for a code is ever updated, browsers won't
  cache the redirect permanently. (In this basic version, codes are
  immutable once created, but 307 is the safer default for a URL shortener.)
- **`create_all()` instead of migrations:** for this scope, tables are
  created automatically on startup. A production system would use Alembic
  for versioned schema migrations.

## Possible Future Improvements

- Rate limiting to prevent abuse
- Custom/user-chosen short codes
- Link expiration dates
- User accounts & authentication so people can manage their own links
- Alembic migrations instead of `create_all()`
