from flask import jsonify


def template(
    data,
    code=500,
):
    return {"errors": data, "status_code": code}


WRONG_LOGIN_CREDS = template(["Username or password are not correct"], code=404)
USER_ALREADY_REGISTERED = template(["User already registered"], code=422)
PASSWORD_CHECK_INVALID = template(
    ["Password and password check must be equal."], code=400
)


class UserExceptions(Exception):
    status_code = 500

    def __init__(self, errors, status_code=None, payload=None):
        Exception.__init__(self)
        self.errors = errors
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_json(self):
        rv = {
            "errors": self.errors,
        }
        return jsonify(rv), self.status_code

    @classmethod
    def user_already_registered(cls):
        return cls(**USER_ALREADY_REGISTERED)

    @classmethod
    def wrong_login_creds(cls):
        return cls(**WRONG_LOGIN_CREDS)

    @classmethod
    def password_check_invalid(cls):
        return cls(**PASSWORD_CHECK_INVALID)
