import pytest
from unittest.mock import patch, MagicMock

from app.legacy.utilgeo import UtilGeo


class TestUtilGeo:
    @patch.dict("os.environ", {"GEO_API_KEY": "geo123", "GEO_API_URL": "https://geo.example.com"})
    @patch("app.legacy.utilgeo.requests.get")
    def test_send_request_get(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"data": "ok"})
        geo = UtilGeo()
        resp, code = geo.send_request(MagicMock(method="GET", data=b""), "/test")
        assert code == 200
        assert resp["data"] == "ok"

    @patch.dict("os.environ", {"GEO_API_KEY": "geo123", "GEO_API_URL": "https://geo.example.com"})
    @patch("app.legacy.utilgeo.requests.post")
    def test_send_request_post(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {"created": True})
        req = MagicMock(method="POST", data=b'{"key": "val"}')
        req.get_json.return_value = {"key": "val"}
        geo = UtilGeo()
        resp, code = geo.send_request(req, "/create")
        assert code == 201

    @patch.dict("os.environ", {"GEO_API_KEY": "geo123", "GEO_API_URL": "https://geo.example.com"})
    def test_send_request_unsupported_method(self):
        geo = UtilGeo()
        req = MagicMock(method="DELETE", data=b"")
        resp, code = geo.send_request(req, "/del")
        assert code == 401
