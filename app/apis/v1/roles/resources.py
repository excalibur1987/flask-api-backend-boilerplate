from flask_jwt_extended import jwt_required
from flask_restx import Resource, fields
from flask_restx.reqparse import RequestParser

from app.database import db
from app.exceptions import InvalidUsage
from app.utils.decorators import has_roles
from app.utils.extended_objects import ExtendedNameSpace
from app.utils.helpers import argument_list_type

from ..users.models import User, UserRoles
from ..users.resources import user_model
from .models import Role

api = ExtendedNameSpace("roles", description="Roles operations")


roles_model = api.model(
    "Role",
    {
        "id": fields.Integer(),
        "name": fields.String(),
        "description": fields.String(),
        "users": fields.List(
            fields.Nested(user_model, skip_none=True),
            attribute=lambda role: User.query.join(
                UserRoles, UserRoles.user_id == User.id
            )
            .with_entities(User.id.label("id"), User.username.label("username"))
            .filter(UserRoles.role_id == role.id)
            .all(),
        ),
    },
)

role_parser_required = RequestParser()
role_parser_required.add_argument(
    "name", required=True, location="form", type=str
).add_argument("description", required=True, location="form", type=str)


role_parser = RequestParser()
role_parser.add_argument("name", location="form", type=str).add_argument(
    "description", location="form", type=str
)


class RolesResource(Resource):
    @jwt_required()
    @has_roles("admin")
    @api.marshal_list_with(roles_model, envelope="data")
    def get(self):

        return Role.query.all()

    @jwt_required()
    @has_roles("admin")
    @api.marshal_list_with(roles_model)
    @api.expect(role_parser_required)
    def post(self):
        args = role_parser.parse_args()
        new_role = Role(**args)
        new_role.save()

        return new_role


user_ids_parser = api.parser()
user_ids_parser.add_argument(
    "users",
    type=argument_list_type(int),
    required=True,
    location="json",
    help="A list of users' ids.",
)

users_ids_model = api.model("users_ids", {"users": fields.List(fields.Integer)})


@api.param("role_id", "role's id", type=int)
class RoleResource(Resource):
    @jwt_required()
    @has_roles("admin")
    @api.marshal_with(roles_model)
    def get(self, role_id: int):

        return Role.get(role_id)

    @jwt_required()
    @has_roles("admin")
    @api.marshal_with(roles_model)
    @api.expect(users_ids_model, validate=True)
    def post(self, role_id: int):
        role_ = Role.get(role_id)

        args = user_ids_parser.parse_args()
        if User.query.filter(User.id.in_(args.get("users"))).count() != len(
            args.get("users")
        ):
            raise InvalidUsage.custom_error("Can't add these users", 401)
        db.session.add_all(
            [UserRoles(user_id=user_id, role=role_) for user_id in args["users"]]
        )

        db.session.commit()

        return role_

    @jwt_required()
    @api.expect(role_parser)
    @has_roles("admin")
    @api.marshal_with(roles_model)
    def put(self, role_id: int):
        args = role_parser.parse_args()
        role: Role = Role.query.filter(Role.id == role_id).first_or_404()
        role.update(**args, ignore_none=True)

        return role


api.add_resource(RolesResource, "/")
api.add_resource(RoleResource, "/<role_id>")
