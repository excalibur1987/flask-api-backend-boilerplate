from functools import wraps
from typing import Callable, Iterable, List, Union

from app.exceptions import InvalidUsage
from flask import g
from flask_principal import Identity, Permission, RoleNeed


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


def has_roles(*args: Iterable[str]):
    roles = [
        (
            Permission(RoleNeed(role))
            if not isinstance(role, list)
            else [Permission(RoleNeed(role_)) for role_ in role]
        )
        for role in args
    ]

    def wrapper(fn: Callable):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            identity: Identity = g.identity
            if not check_roles(identity=identity, roles=roles):
                raise InvalidUsage.user_not_authorized()
            return fn(*args, **kwargs)

        return wrapped

    return wrapper
