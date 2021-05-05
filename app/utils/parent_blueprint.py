from typing import List

from flask.blueprints import Blueprint


class ParentBP(object):
    name: str
    url_prefix: str
    subdomain: str
    blueprints: List[Blueprint]

    def __init__(self, name="", url_prefix="", subdomain="") -> None:
        self.name = name
        self.url_prefix = url_prefix
        self.subdomain = subdomain
        self.blueprints = []

    def register_blueprint(self, bp: Blueprint) -> None:
        bp.name = self.name + "-" + bp.name
        bp.url_prefix = self.url_prefix + (bp.url_prefix or "")
        if self.subdomain:
            bp.subdomain = self.subdomain
        self.blueprints.append(bp)
