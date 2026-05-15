from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from flask_httpauth import HTTPBasicAuth
from app.extensions import csrf, auth, cors


class TestExtensions:
    def test_csrf_is_instance(self):
        assert isinstance(csrf, CSRFProtect)

    def test_auth_is_instance(self):
        assert isinstance(auth, HTTPBasicAuth)

    def test_cors_is_instance(self):
        assert isinstance(cors, CORS)
