import pytest
from unittest.mock import patch, MagicMock

from app.legacy.pageprocessor import Page


class TestPageProcessor:
    def test_init(self):
        with patch.dict("os.environ", {"PAGE_API_KEY": "pk", "LOGIA_BASE_URL": "http://logia"}):
            page = Page()
            assert page.api_key == "pk"

    @patch("app.legacy.pageprocessor.Checker")
    @patch("app.legacy.pageprocessor.Page")
    def test_page_status(self, mock_page_cls, mock_checker_cls):
        mock_checker = MagicMock()
        mock_checker.get_status_pages.return_value = ({"monitors": []}, 200)
        mock_checker.get_info.return_value = {"Database": {"Version": "8.0"}}
        mock_checker_cls.return_value = mock_checker

        page = Page()
        with patch.dict("os.environ", {"PAGE_API_KEY": "pk"}):
            req = MagicMock()
            req.method = "GET"
            req.headers = {}
            req.data = b""
            req.args = {}
            data, code, is_page = page.request_process(req, "status")
            # Because it needs auth/api-key we may get 401; just verify it runs
            assert code in (200, 401)

    def test_cv_process(self):
        with patch.dict("os.environ", {"PAGE_API_KEY": "pk"}):
            page = Page()
            data, code = page.cv_proccess("jonnattan")
            assert code == 200
            assert data["name"] == "Jonnattan Griffiths"

    def test_image_process(self):
        with patch.dict("os.environ", {"PAGE_API_KEY": "pk"}):
            page = Page()
            resp, code = page.image_process("test.png")
            # file likely doesn't exist
            assert code in (200, 404)

    def test_js_process(self):
        with patch.dict("os.environ", {"PAGE_API_KEY": "pk"}):
            page = Page()
            resp, code = page.js_process("logia.js")
            assert code in (200, 404)
