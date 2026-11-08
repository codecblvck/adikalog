import os

from flask import Flask

from config import configs
from app.extensions import db, migrate, crsf
from app.blueprints_reg import register_bluprints


def create_app(config_name=None):
    config_name = config_name or os.environ.get("APP_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY is not set")

    db.init_app(app)
    migrate.init_app(app, db)
    crsf.init_app(app)

    from app import models as models

    register_bluprints(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}
    return app
