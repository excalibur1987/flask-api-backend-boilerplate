from flask import g
from flask_principal import Identity

from .decorators import has_roles
from .extended_flask import ExtendedFlask
from .file_storage import FileStorage
from .helpers import chain, create_api
from .parent_blueprint import ParentBP
from .url_w_args import UrlWArgs


class GlobalObject(object):
    identity: Identity


g: GlobalObject
