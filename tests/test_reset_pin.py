from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.extensions import db
from app.models import User


def make_user(app, name="ada", pin="1357", failed_attempts=0, locked=False):
    with app.app_context():
        user = User(name=name, failed_attempts=failed_attempts)
        user.pin = pin
        if locked:
            user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
        db.session.add(user)
        db.session.commit()


def get_user(app, name="ada"):
    return db.session.scalar(select(User).where(User.name == name))


def run_reset_pin(app, text):
    return app.test_cli_runner().invoke(args=["reset-pin"], input=text)


def test_reset_pin_replaces_the_old_pin(app):
    make_user(app)

    result = run_reset_pin(app, "ada\n2468\n2468\n")

    assert result.exit_code == 0
    assert "PIN reset for ada" in result.output
    assert "2468" not in result.output
    with app.app_context():
        user = get_user(app)
        assert user.check_pin("2468")
        assert not user.check_pin("1357")


def test_reset_pin_clears_the_lock(app):
    make_user(app, failed_attempts=5, locked=True)

    result = run_reset_pin(app, "ada\n2468\n2468\n")

    assert result.exit_code == 0
    with app.app_context():
        user = get_user(app)
        assert user.failed_attempts == 0
        assert user.locked_until is None


def test_reset_pin_matches_name_with_different_case(app):
    make_user(app)

    result = run_reset_pin(app, "  ADA \n2468\n2468\n")

    assert result.exit_code == 0
    with app.app_context():
        assert get_user(app).check_pin("2468")


def test_reset_pin_unknown_user_is_rejected(app):
    result = run_reset_pin(app, "ghost\n")

    assert result.exit_code != 0
    assert "No such user" in result.output


def test_weak_pin_changes_nothing(app):
    make_user(app, failed_attempts=5, locked=True)

    result = run_reset_pin(app, "ada\n1234\n1234\n")

    assert result.exit_code != 0
    with app.app_context():
        user = get_user(app)
        assert user.check_pin("1357")
        assert user.failed_attempts == 5
        assert user.locked_until is not None


def test_mismatched_confirmation_changes_nothing(app):
    make_user(app)

    result = run_reset_pin(app, "ada\n2468\n9753\n")

    assert result.exit_code != 0
    with app.app_context():
        assert get_user(app).check_pin("1357")
