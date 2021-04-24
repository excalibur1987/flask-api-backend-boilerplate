from typing import Type

from flask import Flask

from app.blueprints import register_blueprints
from app.commands import register_commands
from app.extensions import register_extensions
from app.request_handlers import register_handlers
from app.settings import Config
from app.utils import chain


def create_app(config_object: Type[Config]) -> Flask:

    app = Flask(__name__)
    app.config.from_object(config_object)
    chained_function = chain(
        register_commands, register_blueprints, register_extensions, register_handlers
    )
    app = chained_function(app)

    return app
