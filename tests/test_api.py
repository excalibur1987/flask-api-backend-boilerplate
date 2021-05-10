import os

import pytest
from flask.testing import FlaskClient

from app import create_app
from app.database import db
from app.settings import TestConfig

from .helpers import USERS


@pytest.fixture
def client():
    db_location = os.path.join(os.getcwd(), "tests", "test_db.db")
    open(db_location, "w")

    app = create_app(TestConfig)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:////{db_location}"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            USERS.create_admin()
            USERS.create_user()
        yield client

    os.unlink(db_location)


def test_login(client: FlaskClient):

    rv = client.post(
        "/v1/users/login",
        data=dict(username=USERS.USER["username"], password=USERS.ADMIN["password"]),
    )

    res_json = rv.get_json()

    assert (
        res_json["username"].lower() == USERS.USER["username"] and "token" in res_json
    )
