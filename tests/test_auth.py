from datetime import UTC, datetime, timedelta

from app.extensions import db
from app.models import User
from app.auth.service import is_locked, record_wrong_pin, reset_attempts

SET_TIME = timedelta(minutes=15)
FUTURE_TIME = SET_TIME + datetime.now(UTC)
PAST_TIME = datetime.now(UTC) - SET_TIME


def instant_user():
    user = User(name="adika")
    user.pin = "7070"
    return user


def test_locked_until_set_none():
    user = instant_user()
    user.failed_attempts = 3
    user.locked_until = None
    locked = is_locked(user)
    assert not locked
    assert user.failed_attempts == 3
    assert user.locked_until is None


def test_locked_until_set_10min_future():
    user = instant_user()
    user.failed_attempts = 3
    user.locked_until = FUTURE_TIME
    locked = is_locked(user)
    assert locked
    assert user.failed_attempts == 3
    assert user.locked_until == FUTURE_TIME


def test_locked_until_set_10min_past():
    user = instant_user()
    user.failed_attempts = 3
    user.locked_until = PAST_TIME
    locked = is_locked(user)
    assert not locked
    assert user.failed_attempts == 0
    assert user.locked_until is None


# test record wrong pin auth services
def test_one_wrong_pin(user):
    record_wrong_pin(user)

    db.session.rollback()
    db.session.refresh(user)

    assert user.failed_attempts == 1
    assert user.locked_until is None


def test_fifth_wrong_pin(user):
    user.failed_attempts = 4
    before = datetime.now(UTC)
    record_wrong_pin(user)
    after = datetime.now(UTC)

    db.session.rollback()
    db.session.refresh(user)

    assert user.failed_attempts == 5
    assert user.locked_until >= before + SET_TIME
    assert user.locked_until <= after + SET_TIME


def test_count_committed(user):
    record_wrong_pin(user)

    db.session.rollback()
    db.session.refresh(user)
    assert user.failed_attempts == 1


def test_expired_lock_to_reset(user):
    user.failed_attempts = 5
    user.locked_until = datetime.now(UTC) - timedelta(minutes=1)
    is_locked(user)
    record_wrong_pin(user)

    db.session.rollback()
    db.session.refresh(user)

    assert user.failed_attempts == 1


# test reset attempts
def test_failed_user_cleared_saved(user):
    user.failed_attempts = 3
    user.locked_until = FUTURE_TIME
    db.session.commit()

    reset_attempts(user)

    db.session.rollback()
    db.session.refresh(user)

    assert user.failed_attempts == 0
    assert user.locked_until is None


def test_clean_user_stay_clean(user):
    reset_attempts(user)
    db.session.rollback()
    db.session.refresh(user)

    assert user.failed_attempts == 0
    assert user.locked_until is None


def test_failed_user_come_clean_cleared_and_saved(user):
    user.failed_attempts = 5
    user.locked_until = datetime.now(UTC) - timedelta(minutes=1)
    db.session.commit()

    is_locked(user)
    reset_attempts(user)

    db.session.rollback()
    db.session.refresh(user)

    assert user.failed_attempts == 0
    assert user.locked_until is None


def test_is_modified_demo(user):
    # Part 1: clean user
    db.session.commit()
    user.failed_attempts = 0
    user.locked_until = None
    print("clean user, is_modified:", db.session.is_modified(user))

    # Part 2: the trap case
    user.failed_attempts = 5
    user.locked_until = datetime.now(UTC) - timedelta(minutes=1)
    db.session.commit()

    is_locked(user)
    print("after is_locked, is_modified:", db.session.is_modified(user))
