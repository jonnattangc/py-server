import pytest
from unittest.mock import patch, MagicMock

from app.legacy.ucc import Ucc


class TestUcc:
    @patch("app.legacy.ucc.pymysql.connect")
    def test_init(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        with patch.dict("os.environ", {"UCC_API_KEY": "ucc_key"}):
            ucc = Ucc()
            assert ucc.api_key == "ucc_key"

    @patch("app.legacy.ucc.pymysql.connect")
    def test_get_info(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "rut": "123", "name": "Juan", "address": "Calle", "comercial_address": "Oficina",
            "mobile": "+569", "commune": "Stgo", "mail": "juan@example.com", "birth": "1990-01-01 00:00:00"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        with patch.dict("os.environ", {"UCC_API_KEY": "ucc_key"}):
            ucc = Ucc()
            data = ucc.get_info("123")
            assert data["rut"] == "123"
            assert data["name"] == "Juan"

    @patch("app.legacy.ucc.pymysql.connect")
    def test_request_process_unauthorized(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        with patch.dict("os.environ", {"UCC_API_KEY": "ucc_key"}):
            ucc = Ucc()
            req = MagicMock()
            req.headers = {}
            req.data = b""
            req.method = "POST"
            data, code = ucc.request_process(req, "documents/sign")
            assert code == 401
