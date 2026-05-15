import pytest
from unittest.mock import patch, MagicMock

from app.legacy.security import Security


class TestSecurityLegacy:
    @patch("app.legacy.security.pymysql.connect")
    def test_verify_user_pass_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        from werkzeug.security import generate_password_hash
        mock_cursor.fetchall.return_value = [{"username": "jonn", "password": generate_password_hash("pass")}]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        sec = Security()
        result = sec.verifiyUserPass("jonn", "pass")
        assert result == "jonn"

    @patch("app.legacy.security.pymysql.connect")
    def test_verify_user_pass_wrong_password(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        from werkzeug.security import generate_password_hash
        mock_cursor.fetchall.return_value = [{"username": "jonn", "password": generate_password_hash("pass")}]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        sec = Security()
        result = sec.verifiyUserPass("jonn", "wrong")
        assert result is None

    @patch("app.legacy.security.pymysql.connect")
    def test_generate_user(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        sec = Security()
        sec.generateUser("newuser", "newpass")
        mock_conn.commit.assert_called()
