import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import MagicMock, patch

from app import create_app


@pytest.fixture
def app():
    """Application factory fixture."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
    })
    return app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def mock_pymysql():
    """Patch pymysql.connect to return a mock connection."""
    with patch("pymysql.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_connect, mock_conn, mock_cursor


@pytest.fixture(autouse=True)
def patch_auth():
    """Auto-patch auth verify so blueprint tests don't need real DB creds."""
    with patch("app.api.routes.check.BasicAuthProvider") as mock_provider:
        mock_inst = MagicMock()
        mock_inst.verify.return_value = "testuser"
        mock_provider.return_value = mock_inst
        yield
