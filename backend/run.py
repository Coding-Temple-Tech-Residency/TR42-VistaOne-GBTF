from flask import Flask

from app import create_app
from config import DevelopmentConfig

app: Flask = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run()
