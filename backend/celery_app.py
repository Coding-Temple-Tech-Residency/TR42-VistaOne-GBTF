import os

from celery import Celery  # type: ignore[import-untyped]
from dotenv import load_dotenv

load_dotenv()

celery = Celery(
    "app",
    broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)


def init_celery(app):
    """Bind the Celery instance to a Flask application context."""
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
