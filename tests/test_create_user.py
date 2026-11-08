from sqlalchemy import func, select

from app.extensions import db
from app.models import User


def run_create_user(app, text):
    return app.test_cli_runner().invoke(args=["create-user"], input=text)


def count_users(app):
    with app.app_context():
        return db.session.scalar(select(func.count()).select_from(User))


def test_create_user_saves_hashed_pin(app):
    result = run_create_user(app, "Ada\n1357\n1357\n")

    assert result.exit_code == 0
    assert "Created user ada" in result.output
    assert "1357" not in result.output

    with app.app_context():
        user = db.session.scalar(select(User).where(User.name == "ada"))
        assert user is not None
        assert user.pin_hash != "1357"
        assert user.check_pin("1357")


def test_duplicate_name_is_rejected(app):
    run_create_user(app, "ada\n1357\n1357\n")
    result = run_create_user(app, "ada\n")

    assert result.exit_code != 0
    assert "already exists" in result.output
    assert count_users(app) == 1


def test_duplicate_name_with_different_case_and_spaces_is_rejected(app):
    run_create_user(app, "ada\n1357\n1357\n")
    result = run_create_user(app, "  ADA \n")

    assert result.exit_code != 0
    assert "already exists" in result.output
    assert count_users(app) == 1


def test_weak_pin_is_rejected(app):
    result = run_create_user(app, "ada\n1234\n1234\n")

    assert result.exit_code != 0
    assert count_users(app) == 0


def test_mismatched_pin_confirmation_creates_nothing(app):
    result = run_create_user(app, "ada\n1357\n2468\n")

    assert result.exit_code != 0
    assert count_users(app) == 0
