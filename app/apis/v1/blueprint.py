from app.utils.parent_blueprint import ParentBP

from .users.resources import blueprint as user_bp

api_v1 = ParentBP("v1", url_prefix="/v1")

api_v1.register_blueprint(user_bp)
