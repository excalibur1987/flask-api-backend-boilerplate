from flask import Blueprint
from flask_restful import Api, Resource, marshal_with

from .models import User
from .serializers import user_serializer

blueprint = Blueprint("users", __name__)


api = Api(blueprint)


class UserResource(Resource):
    @marshal_with(user_serializer)
    def get(self, id):
        return User.get(id)


api.add_resource(UserResource, "/user/<int:id>")
