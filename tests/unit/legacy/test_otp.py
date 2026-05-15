import pytest
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash

from app.legacy.otp import Otp


class TestOtp:
    @patch("app.legacy.otp.pymysql.connect")
    def test_get_random_otp(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        otp = Otp()
        val, ref = otp.getRandomOtp(6)
        assert len(val) == 6
        assert len(ref) > 0

    @patch("app.legacy.otp.pymysql.connect")
    def test_create_otp(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        otp = Otp()
        val, ref = otp.createOtp(mobile="+569", duration_min=5, len=6)
        assert val is not None
        assert ref is not None
        mock_conn.commit.assert_called()

    @patch("app.legacy.otp.pymysql.connect")
    def test_validate_otp_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Not expired
        mock_cursor.fetchall.return_value = [{
            "otp": generate_password_hash("123456"),
            "status": "PENDING",
            "expirate_at": "2099-12-31 23:59:59"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        otp = Otp()
        valid, reason = otp.validateOtp("ref-1", "123456")
        assert valid is True
        assert reason == "OTP Completamente valida"

    @patch("app.legacy.otp.pymysql.connect")
    def test_validate_otp_expired(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "otp": generate_password_hash("123456"),
            "status": "PENDING",
            "expirate_at": "2000-01-01 00:00:00"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        otp = Otp()
        valid, reason = otp.validateOtp("ref-1", "123456")
        assert valid is False
        assert "expirada" in reason

    @patch("app.legacy.otp.pymysql.connect")
    def test_burn_otp(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        otp = Otp()
        otp.burnOtp("ref-1", True, 1)
        mock_conn.commit.assert_called()

    @patch("app.legacy.otp.pymysql.connect")
    def test_mail_otp_validate(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "otp": generate_password_hash("123456"),
            "ref": "ref-1",
            "expirate_at": "2099-12-31 23:59:59"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        otp = Otp()
        valid, ref = otp.mailOtpValidate("test@example.com", "123456")
        assert valid is True
        assert ref == "ref-1"
