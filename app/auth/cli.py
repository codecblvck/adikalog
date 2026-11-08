import click
from sqlalchemy.exc import IntegrityError

from app.auth import auth_bp
from app.auth.service import get_user_by_name
from app.auth.validators import validate_name, validate_pin
from app.auth.service import reset_attempts
from app.extensions import db
from app.models import User


@auth_bp.cli.command("create-user")
def create_user():
    """Create a user with a name and a 4 digit PIN."""
    try:
        name = validate_name(click.prompt("Name"))
    except ValueError as error:
        raise click.ClickException(str(error))

    if get_user_by_name(name) is not None:
        raise click.ClickException(f"User '{name}' already exists.")

    pin = click.prompt("PIN", hide_input=True, confirmation_prompt=True)
    try:
        validate_pin(pin)
    except ValueError as error:
        raise click.ClickException(str(error))

    user = User(name=name)
    user.pin = pin
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise click.ClickException(f"User '{name}' already exists.")

    click.echo(f"Created user {name}")


@auth_bp.cli.command("reset-pin")
def reset_pin():
    """Set a new PIN for an existing user and clear any lock."""
    name = click.prompt("Name")
    user = get_user_by_name(name)
    if user is None:
        raise click.ClickException("No such user.")

    pin = click.prompt("New PIN", hide_input=True, confirmation_prompt=True)
    try:
        validate_pin(pin)
    except ValueError as error:
        raise click.ClickException(str(error))

    user.pin = pin
    reset_attempts(user)
    click.echo(f"PIN reset for {user.name}")
