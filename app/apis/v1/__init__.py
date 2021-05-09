from flask_restx import Api

from .users import api as user_api

api_v1 = Api(
    title="Backend Api",
    authorizations={
        "apikey": {"type": "apiKey", "in": "header", "name": "X-CSRF-TOKEN"}
    },
    security="apikey",
)

api_v1.add_namespace(user_api, "/v1")
