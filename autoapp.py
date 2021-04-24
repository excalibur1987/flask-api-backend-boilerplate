import os

from app import create_app
from app.settings import DevConfig, ProdConfig

config = (
    DevConfig if os.getenv("FLASK_ENV", "development") == "development" else ProdConfig
)

app = create_app(config_object=config)
