import pytest
from unittest.mock import patch, MagicMock

from app.legacy.captcha import Captcha


class TestCaptcha:
    @patch.dict("os.environ", {"HCAPTCHA_SECRET_KEY": "hc_secret", "RECAPTCHA_SECRET_KEY": "rc_secret"})
    def test_init(self):
        cap = Captcha()
        assert cap.google_secret == "rc_secret"
        assert cap.hcaptcha_secret == "hc_secret"

    @patch.dict("os.environ", {"HCAPTCHA_SECRET_KEY": "hc_secret"})
    @patch("app.legacy.captcha.requests.post")
    def test_hcaptcha_process_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"success": True})
        cap = Captcha()
        data, code = cap.hcaptcha_process({"token": "tok", "sitekey": "site"})
        assert code == 200
        assert data["success"] is True

    @patch.dict("os.environ", {"HCAPTCHA_SECRET_KEY": "hc_secret"})
    def test_hcaptcha_process_none_token(self):
        cap = Captcha()
        data, code = cap.hcaptcha_process({"token": "None", "sitekey": "None"})
        assert code == 409

    @patch.dict("os.environ", {"RECAPTCHA_SECRET_KEY": "rc_secret"})
    @patch("app.legacy.captcha.requests.get")
    def test_google_captcha_success(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"success": True})
        from flask import Flask, request
        app = Flask(__name__)
        with app.test_request_context("/?token=tok"):
            cap = Captcha()
            data, code = cap.google_captcha(request)
            assert code == 200
            assert data["success"] is True
