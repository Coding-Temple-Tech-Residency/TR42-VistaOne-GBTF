FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir gunicorn==21.2.0 \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# ---------- production web server ----------
FROM base AS web
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]

# ---------- celery worker ----------
FROM base AS worker
CMD ["celery", "-A", "celery_app.celery", "worker", "--loglevel=info", "--concurrency=2"]

# ---------- celery beat (optional scheduler) ----------
FROM base AS beat
CMD ["celery", "-A", "celery_app.celery", "beat", "--loglevel=info"]
