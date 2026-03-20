# TR42 VistaOne GBTF — Field Contractor Platform

## Project Overview

The Field Contractor platform solves the critical problem of inefficiency, lack of transparency, and fraud vulnerability in oil and gas field operations. Currently, many small to mid-sized operators rely on manual, paper-based ticketing systems that are:

- **Laborious and error-prone** — Paper tickets get lost, damaged, or illegible
- **Difficult to verify** — No way to confirm work was actually performed at the correct location
- **Vulnerable to fraud** — Phantom employees, inflated hours, and false billing are hard to detect
- **Expensive** — Existing solutions require $8,000+ hardware or expensive enterprise software

Our solution digitizes the entire workflow using standard smartphones, making it affordable and accessible.

## Target Users

| User Role | Description | Primary Need |

|---|---|---|
| **Field Contractor** | Drivers and field workers performing on-site services | Easy job execution, offline capability, clear instructions |
| **Vendor Manager** | Dispatchers and managers at service companies | Track contractor work, review anomalies, manage billing |
| **Operator Admin** | Oil and gas company representatives | Verify work was performed, audit field operations, approve payments |

---

## Tech Stack

### Backend

| Category | Technology |

|---|---|
| **Language** | Python 3.12 |
| **Framework** | Flask 2.3.2 |
| **Database** | PostgreSQL 16 + PostGIS (GeoAlchemy2 0.13.1) |
| **ORM** | SQLAlchemy 2.0.17 / Flask-SQLAlchemy 3.0.5 |
| **Migrations** | Alembic 1.11.1 / Flask-Migrate 4.0.4 |
| **Authentication** | JWT (Flask-JWT-Extended 4.5.2) — HS256, 30 min access / 7 day refresh |
| **Password Hashing** | Werkzeug scrypt |
| **Validation** | Marshmallow 3.19.0 / marshmallow-sqlalchemy 0.29.0 |
| **Rate Limiting** | Flask-Limiter 3.3.1 (5/min login, 60/min global) |
| **Caching** | Flask-Caching 2.0.2 with Redis backend |
| **Task Queue** | Celery 5.3.1 with Redis broker |
| **WSGI Server** | Gunicorn 21.2.0 |
| **CORS** | Flask-CORS 4.0.0 (restricted to configured origins) |

### Mobile App

| Category | Technology |

|---|---|
| **Framework** | React Native |
| **State Management** | Context API |
| **Maps** | React Native Maps |
| **HTTP Client** | Axios |

### Infrastructure

| Category | Technology |

|---|---|
| **Containerization** | Docker (multi-stage Dockerfile) |
| **Orchestration** | Docker Compose |
| **CI/CD** | GitHub Actions (lint → type-check → test → build → deploy) |
| **Container Registry** | GitHub Container Registry (ghcr.io) |

---

## Backend Architecture

```markdown
backend/
├── config.py                  # App configuration (env-var driven)
├── celery_app.py              # Celery factory + init_celery()
├── wsgi.py                    # Production entry point (Gunicorn)
├── run.py                     # Development entry point
├── Dockerfile                 # Multi-stage: web / worker / beat
├── requirements.txt
├── app/
│   ├── __init__.py            # create_app() factory
│   ├── extensions.py          # db, migrate, jwt, limiter, cache
│   ├── api/                   # 10 Blueprint route modules
│   │   ├── auth.py            # Login, token refresh
│   │   ├── contractors.py     # Contractor profile (me)
│   │   ├── issues.py          # Issue reporting
│   │   ├── jobs.py            # Job listing & details (cached)
│   │   ├── photos.py          # Photo upload
│   │   ├── submissions.py     # Job submissions
│   │   ├── sync.py            # Offline sync endpoint
│   │   ├── tasks.py           # Task execution
│   │   ├── vendors.py         # Vendor CRUD + sync (cached)
│   │   └── visits.py          # Site visit check-in/out
│   ├── middleware/
│   │   ├── auth.py            # JWT auth helpers
│   │   └── error_handler.py   # Centralized JSON error responses
│   ├── models/                # 22 SQLAlchemy models
│   ├── schemas/               # Marshmallow schemas
│   ├── services/              # Business logic layer
│   │   ├── audit_service.py
│   │   ├── auth_service.py
│   │   ├── biometric_service.py
│   │   ├── notification_service.py
│   │   ├── sync_service.py
│   │   └── vendor_sync_service.py
│   ├── tasks/                 # Celery tasks
│   │   └── vendor_tasks.py    # Async vendor sync (3 retries, 60s delay)
│   └── utils/
│       ├── geo.py             # Geospatial helpers
│       ├── logger.py          # get_logger() factory
│       ├── rls.py             # Row-level security
│       └── validators.py      # Input validation utilities
├── migrations/
│   └── versions/
│       └── 001_initial_schema.py
└── tests/
    ├── conftest.py            # Fixtures (PostGIS, JWT tokens)
    ├── test_api/
    │   └── test_auth.py       # 14 passing tests
    └── test_models/
```

### Data Models (22 tables)

Contractors, contractor credentials, contractor devices, contractor insurance, contractor sessions, vendors, jobs, job assignments, job responses, job completions, tasks, task executions, site visits, issues, photos, submissions, progress updates, biometric verifications, notification preferences, audit log (partitioned), local sync queue (partitioned), vendor sync queue.

Key features: PostGIS geography columns, GIN indexes on TSVECTOR search columns, 31 foreign-key indexes, partitioned tables for audit and sync data.

---

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16+ with PostGIS extension
- Redis 7+
- (Optional) Docker & Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/TR42-VistaOne-GBTF.git
cd TR42-VistaOne-GBTF
```

### 2. Backend Setup (Local)

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials, secret keys, etc.
```

### 3. Environment Variables

Copy `.env.example` and fill in required values:

```env
# --- Required ---
SECRET_KEY=<random-string>
JWT_SECRET_KEY=<random-string>
DATABASE_URL=postgresql://user:password@localhost:5432/vistaone_gbtf

# --- Optional (tests) ---
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/vistaone_gbtf_test

# --- Optional (integrations) ---
MAPBOX_ACCESS_TOKEN=
VENDOR_API_BASE_URL=https://api.vendor.com
VENDOR_API_KEY=

# --- CORS ---
CORS_ORIGINS=http://localhost:3000,http://localhost:8081

# --- Connection Pool ---
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# --- Redis / Caching ---
REDIS_URL=redis://localhost:6379/0
CACHE_TIMEOUT=300

# --- Celery ---
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 4. Database Setup

```bash
# Create the PostgreSQL database with PostGIS
psql -U postgres -c "CREATE DATABASE vistaone_gbtf;"
psql -U postgres -d vistaone_gbtf -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# Run migrations
flask db upgrade head
```

### 5. Run the Application

```bash
# Development server
python run.py

# Production (Gunicorn)
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app

# Celery worker (separate terminal)
celery -A celery_app.celery worker --loglevel=info --concurrency=2
```

### 6. Docker Setup (Recommended)

From the project root:

```bash
# Start all services (PostgreSQL, Redis, Flask, Celery worker)
docker compose up -d

# View logs
docker compose logs -f web

# Run migrations (runs automatically on first start)
docker compose up migrate

# Stop all services
docker compose down
```

Docker Compose orchestrates five services:

| Service | Image | Purpose |

|---|---|---|
| `db` | postgis/postgis:16-3.4 | PostgreSQL + PostGIS |
| `redis` | redis:7-alpine | Cache + Celery broker |
| `web` | Dockerfile → `web` target | Flask + Gunicorn (port 5000) |
| `migrate` | Dockerfile → `base` target | One-shot `flask db upgrade head` |
| `worker` | Dockerfile → `worker` target | Celery background tasks |

---

## API Endpoints

All endpoints are prefixed with `/api`. JWT required unless noted.

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Auth |

|---|---|---|---|
| POST | `/api/auth/login` | Login and receive JWT tokens | No (rate-limited: 5/min) |
| POST | `/api/auth/refresh` | Refresh access token | Refresh token |

### Contractors (`/api/contractors`)

| Method | Endpoint | Description |

|---|---|---|
| GET | `/api/contractors/me` | Get current contractor profile |
| PUT | `/api/contractors/me` | Update current contractor profile |

### Jobs (`/api/jobs`) — cached (60s)

| Method | Endpoint | Description |

|---|---|---|
| GET | `/api/jobs/` | List jobs |
| GET | `/api/jobs/<job_id>` | Get job details |
| GET | `/api/jobs/<job_id>/assignments` | Get job assignments |

### Vendors (`/api/vendors`) — cached (120s)

| Method | Endpoint | Description |

|---|---|---|
| GET | `/api/vendors/` | List vendors |
| GET | `/api/vendors/<vendor_id>` | Get vendor details |
| POST | `/api/vendors/` | Create vendor |
| PUT | `/api/vendors/<vendor_id>` | Update vendor |
| DELETE | `/api/vendors/<vendor_id>` | Delete vendor |
| POST | `/api/vendors/<vendor_id>/sync` | Trigger async vendor sync |

### Site Visits (`/api/visits`)

| Method | Endpoint | Description |

|---|---|---|
| POST | `/api/visits/` | Create / check in to site visit |
| PUT | `/api/visits/<visit_id>` | Update site visit |
| POST | `/api/visits/<visit_id>/checkout` | Check out of site visit |

### Tasks (`/api/tasks`)

| Method | Endpoint | Description |

|---|---|---|
| POST | `/api/tasks/<task_id>/execute` | Execute a task |

### Issues (`/api/issues`)

| Method | Endpoint | Description |

|---|---|---|
| POST | `/api/issues/` | Report an issue |

### Photos (`/api/photos`)

| Method | Endpoint | Description |

|---|---|---|
| POST | `/api/photos/` | Upload a photo |

### Submissions (`/api/submissions`)

| Method | Endpoint | Description |

|---|---|---|
| POST | `/api/submissions/` | Submit completed work |

### Sync (`/api/sync`)

| Method | Endpoint | Description |

|---|---|---|
| POST | `/api/sync/` | Sync offline data |

### Health Check

| Method | Endpoint | Description | Auth |

|---|---|---|---|
| GET | `/health` | Application health check | No |

---

## Testing

```bash
cd backend

# Run all tests (14 passing)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term --cov-report=html

# Open HTML coverage report
open htmlcov/index.html
```

Tests use an in-process PostGIS database and `SimpleCache` (no Redis required).

---

## Code Quality

```bash
cd backend

# Linting (flake8 — all clean)
flake8 app/ --max-line-length=99 --count --show-source --statistics

# Type checking (mypy — 81 source files, 0 issues)
mypy app/
```

---

## CI/CD Pipeline (GitHub Actions)

Three workflows under `.github/workflows/`:

| Workflow | File | Trigger | Jobs |

|---|---|---|---|
| **CI** | `ci.yml` | Push/PR to `main`/`develop` | Flake8 lint, mypy type-check, pytest (PostGIS + Redis service containers) |
| **Docker** | `docker.yml` | Push to `main` | Build `web` + `worker` images, push to GHCR |
| **Deploy** | `deploy.yml` | After Docker build succeeds, or manual dispatch | SSH to VPS, pull images, run migrations, restart services |

### Required GitHub Secrets

| Secret | Description |

|---|---|
| `DEPLOY_HOST` | VPS IP address or hostname |
| `DEPLOY_USER` | SSH username |
| `DEPLOY_SSH_KEY` | Private SSH key for deploy user |

### Required GitHub Environments

Create `staging` and `production` environments with:

- `APP_URL` variable — the public URL of the deployment
- `DEPLOY_PATH` variable (optional, defaults to `/opt/vistaone`)

---

## Backend Accomplishments

- **22 SQLAlchemy models** with PostGIS geography columns, partitioned tables, GIN/TSVECTOR search indexes, and 31 foreign-key indexes
- **10 API blueprints** with full CRUD, Marshmallow schema validation, and structured JSON error responses
- **JWT authentication** with HS256, 30-min access tokens, 7-day refresh tokens, and scrypt password hashing
- **Security hardening** — rate limiting (5/min login, 60/min global), CORS restricted to configured origins, secure cookies in production, LoginSchema validation
- **Centralized logging** — `get_logger()` factory with environment-aware log levels across all routes and services
- **Centralized error handling** — consistent `{error, status, details}` JSON envelope, global `ValidationError` handler, production-safe stack traces
- **Alembic migrations** — full downgrade/upgrade cycle verified and repeatable
- **Environment-driven config** — all secrets loaded from env vars with `_require_env()` validation; `.env.example` provided
- **Connection pooling** — `SQLALCHEMY_ENGINE_OPTIONS` with configurable pool size, overflow, recycle, and pre-ping
- **Redis caching** — `@cache.cached` on expensive GET endpoints (jobs 60s, vendors 120s), automatic cache invalidation on writes
- **Celery background tasks** — async vendor sync with 3 retries and 60-second retry delay
- **Docker containerization** — multi-stage Dockerfile (web/worker/beat targets), Docker Compose with PostgreSQL, Redis, and healthchecks
- **CI/CD pipeline** — GitHub Actions for linting, type-checking, testing, Docker image builds, and automated deployment
- **Code quality** — flake8 clean (max-line-length=99), mypy clean (81 source files, 0 issues), 14 passing tests

---

## Contributing

### Development Standards

- Write clean, readable, and modular code
- Use clear naming conventions
- Follow consistent formatting and linting practices (flake8, mypy)
- Write meaningful commit messages
- Keep branches organized and avoid pushing broken code to main

### Git Workflow

1. Create feature branch from `main`
2. Implement changes with clear commits
3. Push branch and create PR
4. Request review from team members
5. Address feedback and merge

---

## Intellectual Property Notice

This project was created as part of a Coding Temple Tech Residency. All work produced during the residency is considered the intellectual property of Coding Temple or the sponsoring employer, unless otherwise stated in a signed agreement. By contributing to this project, you acknowledge and agree to these terms.

## License

Copyright &copy; 2026 Coding Temple. All rights reserved.

## Team

| Name | Role |

|---|---|
| Justin Wold | Full Stack Backend Head |
| Aldo Emmanuel Pena Herrera | Full Stack Backend |
| Charlie Estrada | Full Stack Frontend Head |
| Hector Gomez | Cybersecurity |

## Contact

For questions or support, please contact the team through GitHub Issues or reach out to your team lead.
