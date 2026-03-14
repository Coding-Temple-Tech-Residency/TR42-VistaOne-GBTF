from flask import Flask
from flask_migrate import Migrate

from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    Migrate(app, db)

    from routes import auth_routes
    app.register_blueprint(auth_routes.bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()