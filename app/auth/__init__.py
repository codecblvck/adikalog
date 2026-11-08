from flask import Blueprint

auth_bp = Blueprint("auth", __name__, cli_group=None)

from app.auth import cli  as cli
