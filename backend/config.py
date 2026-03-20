import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _require_env(key: str) -> str:
    """Return the value of a required environment variable or raise."""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {key}. "
            f"See .env.example for the full list."
        )
    return value


class Config:
    SECRET_KEY = _require_env("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = _require_env("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_ALGORITHM = "HS256"
    MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_ACCESS_TOKEN")
    VENDOR_API_BASE_URL = os.environ.get("VENDOR_API_BASE_URL")
    VENDOR_API_KEY = os.environ.get("VENDOR_API_KEY")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_TIMEOUT", "300"))
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/1"
    )


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _require_env("DATABASE_URL")


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _require_env("DATABASE_URL")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PREFERRED_URL_SCHEME = "https"
    JWT_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://test_user:test_pass@localhost:5432/vistaone_test"
    )
    CORS_ORIGINS = ["*"]
    CACHE_TYPE = "SimpleCache"

    @classmethod
    def validate(cls) -> None:
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError(
                "Missing TEST_DATABASE_URL (or DATABASE_URL) for tests."
            )
