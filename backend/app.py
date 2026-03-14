from flask import Flask
from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from routes import auth_routes
    app.register_blueprint(auth_routes.bp)

    return app
