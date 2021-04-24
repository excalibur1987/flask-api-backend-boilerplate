from typing import Type

from flask import Flask

from app.settings import Config


def create_app(config_object: Type[Config]) -> Flask:

    app = Flask(__name__)
    app.config.from_object(config_object)

    return app
