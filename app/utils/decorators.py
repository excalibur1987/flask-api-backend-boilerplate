from typing import Callable, List, Union

from flask import g
from flask_principal import Identity, Permission, RoleNeed

from app.exceptions import InvalidUsage


def check_roles(
    identity: Identity,
    roles: List[Union[Permission, List[Permission]]],
    optional: bool = False,
) -> bool:
    allowed_roles = [
        (
            role.allows(identity)
            if not isinstance(role, list)
            else check_roles(identity, role, optional=True)
        )
        for role in roles
    ].count(True)

    return allowed_roles > 0 and (allowed_roles == len(roles) or optional)


def has_roles(*args: List[str]):
    roles = [
        (
            Permission(RoleNeed(role))
            if not isinstance(role, list)
            else [Permission(RoleNeed(role_)) for role_ in role]
        )
        for role in args
    ]

    def wrapper(fn: Callable):
        def wrapped(*args, **kwargs):
            identity: Identity = g.identity
            if not check_roles(identity=identity, roles=roles):
                raise InvalidUsage.user_not_authorized()
            return fn(*args, **kwargs)

        wrapped.__doc__ = fn.__doc__
        return wrapped

    return wrapper
