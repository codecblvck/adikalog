from app.auth import auth_bp


def register_bluprints(app):
    app.register_blueprint(auth_bp)
