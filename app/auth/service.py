from datetime import UTC, datetime, timedelta

from sqlalchemy import update,select

from app.extensions import db
from app.models import User
from app.auth.validators import validate_name, validate_pin

MAX_ATTEMPTS = 5
LOCKED_MINUTE = 15
SET_TIME = timedelta(minutes=LOCKED_MINUTE)
FUTURE_TIME = SET_TIME + datetime.now(UTC)
PAST_TIME = datetime.now(UTC) - SET_TIME


def get_user_by_name(name):
    try:
        cleaned = validate_name(name)
    except ValueError:
        return None
    return db.session.scalar(select(User).where(User.name == cleaned))


def is_locked(user):
    if user.locked_until is None:
        return False
    elif user.locked_until > datetime.now(UTC):
        return True
    user.failed_attempts = 0
    user.locked_until = None
    return False


def record_wrong_pin(user):
    attempts = db.session.execute(
        update(User)
        .where(User.id == user.id)
        .values(failed_attempts=User.failed_attempts + 1)
        .returning(User.failed_attempts)
    ).scalar_one()
    if attempts >= MAX_ATTEMPTS:
        db.session.execute(
            update(User)
            .where(User.id == user.id)
            .values(locked_until=SET_TIME + datetime.now(UTC))
        )
    db.session.commit()


def reset_attempts(user):
    user.failed_attempts = 0
    user.locked_until = None
    db.session.commit()
