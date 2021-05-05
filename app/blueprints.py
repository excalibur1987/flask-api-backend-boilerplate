from typing import TYPE_CHECKING

from app.apis.v1.blueprint import api_v1

if TYPE_CHECKING:
    from app.utils import ExtendedFlask


def register_blueprints(app: "ExtendedFlask") -> "ExtendedFlask":
    """A function to register flask blueprint.
    To register blueprints add them like the example
    Example usage:
        from app.blueprints import blueprint
        app.register_blueprint(blueprint)
    Args:
        app (Flask): Flask Application instance

    Returns:
        Flask: Flask Application instance
    """
    app.register_blueprint(api_v1)

    return app
