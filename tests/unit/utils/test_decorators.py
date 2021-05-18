import pytest
from app.exceptions import InvalidUsage
from app.utils import g
from app.utils.decorators import check_roles, has_roles
from flask import Flask
from flask_principal import Identity, Permission, RoleNeed


@pytest.fixture(scope="module")
def admin_role() -> RoleNeed:
    return RoleNeed("admin")


@pytest.fixture(scope="module")
def user_role() -> RoleNeed:
    return RoleNeed("user")


@pytest.fixture(scope="module")
def test_role() -> RoleNeed:
    return RoleNeed("test")


def test_check_roles(admin_role: RoleNeed, user_role: RoleNeed, test_role: RoleNeed):
    """Given an Identity checks validity of a list of permissions"""

    test_identity = Identity(1)

    test_identity.provides.add(admin_role)

    assert check_roles(test_identity, [Permission(admin_role)])
    assert not check_roles(test_identity, [Permission(user_role)])

    test_identity.provides.add(test_role)

    assert check_roles(
        test_identity, [Permission(admin_role), Permission(user_role)], optional=True
    )

    assert check_roles(
        test_identity,
        [Permission(admin_role), [Permission(user_role), Permission(test_role)]],
    )


@has_roles("user")
def add2(a: int, b: int) -> int:
    return a + b


@has_roles("admin")
def add1(a: int, b: int) -> int:

    return a + b


def test_has_roles(test_app: Flask, admin_role: RoleNeed):
    """ "Given a logged-in identity check if they provide these roles"""
    with test_app.app_context():
        test_identity = Identity(1)

        test_identity.provides.add(admin_role)

        g.identity = test_identity

        assert add1(1, 2) == 3

        try:
            _ = add2(1, 2)
        except Exception as e:
            assert isinstance(e, InvalidUsage)
            assert e.status_code == 401
            assert e.errors[0] == "Unauthorized access"
