FROM python:3.12-slim-bullseye AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip wheel bandit safety \
    && pip wheel --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim-bullseye AS runtime-base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-index --find-links=/wheels -r requirements.txt \
    && rm -rf /wheels

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

FROM runtime-base AS web
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]

FROM runtime-base AS worker
CMD ["celery", "-A", "celery_app.celery", "worker", "--loglevel=info", "--concurrency=2"]

FROM runtime-base AS beat
CMD ["celery", "-A", "celery_app.celery", "beat", "--loglevel=info"]
