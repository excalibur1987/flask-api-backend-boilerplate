from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields

from app.utils.decorators import has_roles
from app.utils.extended_objects import ExtendedNameSpace

from .models import Role

api = ExtendedNameSpace("roles", description="Roles operations")

roles_model = api.model(
    "Role", {"name": fields.String(), "description": fields.String()}
)


class RolesResource(Resource):
    @jwt_required()
    @has_roles("admin")
    @api.marshal_list_with(roles_model)
    def get(self):

        return Role.query.all()


api.add_resource(RolesResource, "/roles")
