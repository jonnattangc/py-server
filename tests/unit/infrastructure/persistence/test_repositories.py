import pytest
from unittest.mock import MagicMock, patch

from app.infrastructure.persistence.mysql_repositories import (
    MySqlConnection,
    UserRepository,
    OtpRepository,
)


class TestMySqlConnection:
    def test_connect_success(self, mock_pymysql):
        mock_connect, mock_conn, _ = mock_pymysql
        db = MySqlConnection()
        db.connect()
        assert db.is_connected()
        mock_connect.assert_called_once()

    def test_connect_failure(self):
        with patch("pymysql.connect", side_effect=Exception("boom")):
            db = MySqlConnection()
            db.connect()
            assert not db.is_connected()

    def test_close(self, mock_pymysql):
        _, mock_conn, _ = mock_pymysql
        db = MySqlConnection()
        db.connect()
        db.close()
        mock_conn.close.assert_called_once()
        assert not db.is_connected()

    def test_raw_returns_connection(self, mock_pymysql):
        _, mock_conn, _ = mock_pymysql
        db = MySqlConnection()
        assert db.raw is mock_conn


class TestUserRepository:
    def test_verify_credentials_success(self, mock_pymysql):
        _, mock_conn, mock_cursor = mock_pymysql
        mock_cursor.fetchall.return_value = [
            {"username": "admin", "password": "scrypt:32768:8:1$...$hash"}
        ]
        with patch("app.infrastructure.persistence.mysql_repositories.check_password_hash", return_value=True):
            repo = UserRepository(MySqlConnection())
            result = repo.verify_credentials("admin", "secret")
            assert result == "admin"

    def test_verify_credentials_failure(self, mock_pymysql):
        _, mock_conn, mock_cursor = mock_pymysql
        mock_cursor.fetchall.return_value = []
        repo = UserRepository(MySqlConnection())
        result = repo.verify_credentials("admin", "secret")
        assert result is None

    def test_create_user(self, mock_pymysql):
        _, mock_conn, mock_cursor = mock_pymysql
        repo = UserRepository(MySqlConnection())
        repo.create_user("newuser", "hashedpass")
        mock_conn.commit.assert_called_once()


class TestOtpRepository:
    def test_create(self, mock_pymysql):
        _, mock_conn, mock_cursor = mock_pymysql
        repo = OtpRepository(MySqlConnection())
        data = {
            "create_at": "2024-01-01 00:00:00",
            "expirate_at": "2024-01-01 00:10:00",
            "otp": "hash",
            "ref": "ref-1",
            "mail": None,
            "mobile": "+569",
            "status": "PENDING",
            "channel": "sms",
        }
        repo.create(data)
        mock_conn.commit.assert_called_once()

    def test_find_pending_by_channel_email(self, mock_pymysql):
        _, mock_conn, mock_cursor = mock_pymysql
        mock_cursor.fetchall.return_value = [{"ref": "r1"}]
        repo = OtpRepository(MySqlConnection())
        result = repo.find_pending_by_channel("test@example.com")
        assert len(result) == 1
        assert result[0]["ref"] == "r1"

    def test_find_pending_by_channel_mobile(self, mock_pymysql):
        _, mock_conn, mock_cursor = mock_pymysql
        mock_cursor.fetchall.return_value = [{"ref": "r2"}]
        repo = OtpRepository(MySqlConnection())
        result = repo.find_pending_by_channel("+569")
        assert len(result) == 1

    def test_find_by_reference(self, mock_pymysql):
        _, mock_conn, mock_cursor = mock_pymysql
        mock_cursor.fetchall.return_value = [{"ref": "r3", "status": "PENDING"}]
        repo = OtpRepository(MySqlConnection())
        result = repo.find_by_reference("r3")
        assert result[0]["status"] == "PENDING"

    def test_burn(self, mock_pymysql):
        _, mock_conn, mock_cursor = mock_pymysql
        repo = OtpRepository(MySqlConnection())
        repo.burn("r3", "BURN", 1)
        mock_conn.commit.assert_called_once()
