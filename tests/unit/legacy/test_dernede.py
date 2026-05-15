import pytest
from unittest.mock import patch, MagicMock

from app.legacy.dernede import Dernede


class TestDernede:
    def test_init_reads_keys(self):
        d = Dernede()
        assert d.public_start == "-----BEGIN PUBLIC KEY-----"
        assert d.private_start == "-----BEGIN PRIVATE KEY-----"

    def test_aes_encrypt_decrypt(self):
        with patch.dict("os.environ", {"AES_KEY": "my_secret_key_1234567890123456"}):
            d = Dernede()
            cipher = d.aes_encrypt("hello")
            assert cipher is not None
            clear = d.aes_decrypt(cipher)
            assert clear["message"] == "hello"

    def test_request_process_timeout(self):
        with patch.dict("os.environ", {"AES_KEY": "my_secret_key_1234567890123456"}):
            d = Dernede()
            req = MagicMock()
            req.method = "POST"
            req.get_json.return_value = {"data": "x"}
            data, code = d.requestProcess(req, "timeout")
            assert code == 200
            assert "timeout" in data.get_json()["statusDescription"].lower() or data.get_json()["statusDescription"] == "OK"

    def test_request_process_encrypt(self):
        with patch.dict("os.environ", {"AES_KEY": "my_secret_key_1234567890123456"}):
            d = Dernede()
            req = MagicMock()
            req.method = "POST"
            req.get_json.return_value = {"payload": "data"}
            data, code = d.requestProcess(req, "other")
            assert code == 200
            assert "jwt" in data.get_json()
