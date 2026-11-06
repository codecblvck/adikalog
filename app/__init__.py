import os

from flask import Flask

from app.extensions import db, migrate
from config import configs


def create_app(config_name=None):
    config_name = config_name or os.environ.get("APP_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(configs[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models as models


    @app.get("/health")
    def health():
        return {"status": "ok"}
    return app
