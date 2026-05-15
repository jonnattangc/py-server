import os
import pytest
from app.config import Config


class TestConfig:
    def test_config_has_required_attributes(self):
        assert hasattr(Config, 'SECRET_KEY')
        assert hasattr(Config, 'HOST_BD')
        assert hasattr(Config, 'PORT_BD')
        assert hasattr(Config, 'USER_BD')
        assert hasattr(Config, 'PASS_BD')
        assert hasattr(Config, 'SCHEMA_BD')

    def test_config_default_values(self):
        assert Config.PORT_BD == 3306
        assert Config.DEBUG is False

    def test_config_paths_exist(self):
        assert os.path.isdir(Config.STATIC_DIR)
        assert os.path.isdir(Config.TEMPLATE_DIR)
        assert os.path.isdir(Config.BASE_DIR)
