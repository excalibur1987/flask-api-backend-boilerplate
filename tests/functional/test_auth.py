from flask import Flask, Response
from flask.testing import FlaskClient

from tests.helpers import ExtendedClient, UserDict


def test_login(client: FlaskClient, site_user: UserDict):

    response: Response = client().post(
        "/v1/users/login",
        data=dict(username=site_user["username"], password=site_user["password"]),
    )

    res_json = response.get_json()

    assert res_json["username"].lower() == site_user["username"] and "token" in res_json


def test_logout(test_app: Flask, client: ExtendedClient, site_user: UserDict):
    from app.apis.v1.users.models import User

    with test_app.app_context():

        user_client = client("user")
        user = User.get(username=site_user["username"])

        rv: Response = user_client.get(f"/v1/users/{user.id}")

        res_json = rv.get_json()
        assert res_json.get("username") == user.username
        rv: Response = user_client.get("/v1/logout")

        assert rv.status_code != 200
