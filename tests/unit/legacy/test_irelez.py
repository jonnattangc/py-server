import pytest
from unittest.mock import patch, MagicMock

from app.legacy.irelez import Irelez


class TestIrelez:
    @patch("app.legacy.irelez.pymysql.connect")
    def test_init(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        zlr = Irelez()
        assert zlr.is_connect()

    @patch("app.legacy.irelez.pymysql.connect")
    def test_get_config(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "environment": "prod", "request": "req", "response": "resp",
            "enabled": 1, "hash": "h", "id": 1,
            "coverage_key": "cov", "ot_key": "ot", "geo_key": "geo", "base_url": "https://api.example.com"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        zlr = Irelez()
        config = zlr.get_config()
        assert config["environment"] == "prod"
        assert config["url"] == "https://api.example.com"

    @patch("app.legacy.irelez.pymysql.connect")
    @patch("app.legacy.irelez.requests.get")
    def test_request_process_get(self, mock_get, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "environment": "prod", "request": "", "response": "", "enabled": 0,
            "hash": "", "id": 1, "coverage_key": "", "ot_key": "", "geo_key": "", "base_url": "https://api.example.com"
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"ok": True})

        zlr = Irelez()
        req = MagicMock()
        req.method = "GET"
        req.headers = {}
        req.data = b""
        data, code = zlr.request_process(req, "test")
        assert code == 200
