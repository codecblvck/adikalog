import pytest

from flask_migrate import downgrade, upgrade
from sqlalchemy import text
from sqlalchemy.engine import make_url

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")

    db_url = app.config["SQLALCHEMY_DATABASE_URI"]
    if not db_url or not make_url(db_url).database.endswith("_test"):
        raise RuntimeError("Refusing to run: the test database name must end in _test")

    with app.app_context():
        downgrade(revision="base")
        upgrade()

    yield app


@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db.session.execute(text("TRUNCATE users, sales, sale_items RESTART IDENTITY"))
        db.session.commit()

@pytest.fixture(scope="session")
def make_user():
    user = User(name="codecblvck")
    user.pin = "7070"
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def user(app):
    with app.app_context():
        u = User(name="codecblvck")
        u.pin = "7070"
        db.session.add(u)
        db.session.commit()
        yield u  
