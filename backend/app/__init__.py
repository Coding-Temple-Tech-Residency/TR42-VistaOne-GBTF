import os

from flask import Flask
from flask_cors import CORS

from app.extensions import cache, db, jwt, limiter, migrate
from app.middleware.error_handler import register_error_handlers
from celery_app import init_celery
from config import DevelopmentConfig, ProductionConfig, TestingConfig

_config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def create_app(config_object=None):
    app = Flask(__name__)
    if config_object is None:
        env = os.environ.get("FLASK_ENV", "development")
        config_object = _config_map.get(env, DevelopmentConfig)
    app.config.from_object(config_object)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", [])}},
    )
    db.init_app(app)
    migrate.init_app(app, db, compare_type=False)
    jwt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    init_celery(app)

    # Register blueprints
    from app.api import (
        auth,
        contractors,
        issues,
        jobs,
        photos,
        submissions,
        sync,
        tasks,
        vendors,
        visits,
    )

    app.register_blueprint(auth.bp, url_prefix="/api/auth")
    app.register_blueprint(contractors.bp, url_prefix="/api/contractors")
    app.register_blueprint(vendors.bp, url_prefix="/api/vendors")
    app.register_blueprint(jobs.bp, url_prefix="/api/jobs")
    app.register_blueprint(visits.bp, url_prefix="/api/visits")
    app.register_blueprint(tasks.bp, url_prefix="/api/tasks")
    app.register_blueprint(issues.bp, url_prefix="/api/issues")
    app.register_blueprint(photos.bp, url_prefix="/api/photos")
    app.register_blueprint(submissions.bp, url_prefix="/api/submissions")
    app.register_blueprint(sync.bp, url_prefix="/api/sync")

    register_error_handlers(app)

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app
