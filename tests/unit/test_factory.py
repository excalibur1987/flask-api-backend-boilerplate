from app import create_app
from app.settings import TestConfig


def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app(TestConfig).testing
