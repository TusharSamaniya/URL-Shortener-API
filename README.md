# URL Shortener API

A URL shortener built with **FastAPI** and **PostgreSQL**, packaged with Docker for one-command setup. Submit a long URL and get back a short code that redirects to the original.

---

## Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — persistent storage
- **SQLAlchemy** — ORM
- **Pydantic** — request/response validation
- **Docker Compose** — runs the database, API, and frontend together
- **pytest** — automated tests

---

## Project Structure

```
url-shortener/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, routes & CORS
│   │   ├── models.py        # SQLAlchemy ORM model (the `urls` table)
│   │   ├── schemas.py       # Pydantic request/response schemas
│   │   ├── crud.py          # Database access logic
│   │   ├── database.py      # SQLAlchemy engine/session setup
│   │   └── config.py        # Environment-based settings
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── test_api.py          # Automated tests (pytest)
├── frontend/                # Simple HTML/CSS/JS UI, served via nginx
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

The backend follows a layered structure — routes → CRUD → models — to keep the code readable and easy to extend.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/shorten` | Accepts a long URL, returns a short code + short URL |
| `GET` | `/{short_code}` | Redirects (HTTP 307) to the original URL |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive Swagger UI |


---

## How to Run

### Option A — Docker Compose (recommended)

This starts PostgreSQL, the API, and the frontend together with one command:

```bash
docker-compose up --build
```

- API: **http://localhost:8000** (docs at `/docs`)
- Frontend: **http://localhost:5500**

### Option B — Run locally without Docker

Prerequisites: Python 3.11+, a running PostgreSQL instance.

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # adjust DATABASE_URL if needed
uvicorn app.main:app --reload
```

Serve the frontend separately:

```bash
cd frontend
python -m http.server 5500
```

Then open **http://localhost:5500**.

---

## Example Usage

**Shorten a URL:**

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://www.example.com/some/very/long/path"}'
```

Response:

```json
{
  "short_code": "aZ3xQ1",
  "short_url": "http://localhost:8000/aZ3xQ1",
  "original_url": "https://www.example.com/some/very/long/path",
  "created_at": "2026-08-19T10:15:00Z"
}
```

**Use the short URL:**

```bash
curl -L http://localhost:8000/aZ3xQ1
# redirects to https://www.example.com/some/very/long/path
```

---

## Running Tests

```bash
cd backend
pytest
```

---

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/url_shortener` |
| `BASE_URL` | Base URL used to build the returned short URL | `http://localhost:8000` |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins | `http://localhost:5500,http://127.0.0.1:5500` |
| `SHORT_CODE_LENGTH` | Number of characters in generated short codes | `6` |

---

## Docker Images

Pre-built images are available on Docker Hub:

- Backend: `docker pull tusharsamaniya29/url-shortener-backend:latest`
- Frontend: `docker pull tusharsamaniya29/url-shortener-frontend:latest`

## Links

- GitHub: _add your repo link here_
- Docker Hub: _add your Docker Hub repo link here_