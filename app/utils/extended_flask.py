from typing import Any, Union

from flask import Blueprint, Flask

from .parent_blueprint import ParentBP


class ExtendedFlask(Flask):
    def register_blueprint(
        self, blueprint: Union[Blueprint, ParentBP], **options: Any
    ) -> None:
        if isinstance(blueprint, ParentBP):
            for bp in blueprint.blueprints:
                super().register_blueprint(bp, **options)
        else:
            return super().register_blueprint(blueprint, **options)
