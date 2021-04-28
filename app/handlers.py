from typing import TYPE_CHECKING

from flask.app import Flask
from flask_principal import (
    Identity,
    RoleNeed,
    UserNeed,
    identity_changed,
    identity_loaded,
)

from app.exceptions import InvalidUsage

if TYPE_CHECKING:
    from app.blueprints.users.models import User


def on_identity_loaded(sender, identity):
    from app.blueprints.users.models import User

    # Set the identity user object
    user: "User" = User.get(identity.id)
    identity.user = user

    if user:
        # Add the UserNeed to the identity
        identity.provides.add(UserNeed(user.id))

        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides
        for role in user.roles:
            identity.provides.add(RoleNeed(role.name))


def user_identity_lookup(user: "User"):
    return user.id


def user_lookup_callback(_jwt_header, jwt_data):
    from flask import current_app

    from app.blueprints.users.models import User

    identity = jwt_data["user"]
    user = User.get(identity)
    if not user or not user.active:
        raise InvalidUsage.user_not_authorized()
    identity_changed.send(current_app, identity=Identity(identity))

    return user


def register_handlers(app: Flask) -> Flask:
    """A function to register global request handlers.
    To register a handler add them like the example
    Example usage:

        def fn(request: Request):
            pass

        app.before_request(fn)

    Args:
        app (Flask): Flask Application instance

    Returns:
        Flask: Flask Application instance
    """
    identity_loaded.connect_via(app)(on_identity_loaded)

    @app.errorhandler(InvalidUsage)
    def invalid_error_handler(e: InvalidUsage):
        return e.to_json()

    return app
