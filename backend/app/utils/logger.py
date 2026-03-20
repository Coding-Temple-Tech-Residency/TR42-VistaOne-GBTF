import logging
import os
import sys


def _is_production() -> bool:
    return os.environ.get("FLASK_ENV", "development") == "production"


def setup_logging() -> None:
    """Configure root logging once at startup."""
    level = logging.WARNING if _is_production() else logging.DEBUG
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(fmt))

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on repeated calls (e.g. tests)
    if not root.handlers:
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger under the ``app`` hierarchy."""
    return logging.getLogger(f"app.{name}")


# Convenience default logger (kept for backward compatibility)
setup_logging()
logger = get_logger("general")
