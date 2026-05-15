import pytest
from unittest.mock import patch, MagicMock

from app.legacy.sserpxelihc import Sserpxelihc


class TestSserpxelihc:
    @patch("app.legacy.sserpxelihc.pymysql.connect")
    def test_init(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        cxp = Sserpxelihc()
        assert cxp.isConnect()

    @patch("app.legacy.sserpxelihc.pymysql.connect")
    def test_get_config(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "environment": "prod", "request": "req", "response": "resp",
            "enabled": 1, "hash": "h", "id": 1,
            "coverage_key": "cov", "ot_key": "ot", "geo_key": "geo", "base_url": "https://api.example.com",
            "meta_data": None
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        cxp = Sserpxelihc()
        config = cxp.get_config()
        assert config["environment"] == "prod"

    @patch("app.legacy.sserpxelihc.pymysql.connect")
    def test_get_key_by_path(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        cxp = Sserpxelihc()
        config = {"cov": "cov_key", "ot": "ot_key", "geo": "geo_key"}
        assert cxp.get_key_by_path(config, "rating/test") == "cov_key"
        assert cxp.get_key_by_path(config, "transport-orders/test") == "ot_key"
        assert cxp.get_key_by_path(config, "georeference/test") == "geo_key"

    @patch("app.legacy.sserpxelihc.pymysql.connect")
    @patch("app.legacy.sserpxelihc.requests.post")
    def test_request_process_post(self, mock_post, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{
            "environment": "prod", "request": "", "response": "", "enabled": 0,
            "hash": "", "id": 1, "coverage_key": "key", "ot_key": "", "geo_key": "", "base_url": "https://api.example.com",
            "meta_data": None
        }]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"ok": True})

        cxp = Sserpxelihc()
        req = MagicMock()
        req.method = "POST"
        req.headers = {}
        req.data = b'{}'
        req.get_json.return_value = {}
        data, code = cxp.requestProcess(req, "test")
        assert code == 200
