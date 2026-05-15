from unittest.mock import MagicMock, patch
from app.infrastructure.security.basic_auth import BasicAuthProvider


class TestBasicAuthProvider:
    @patch("app.infrastructure.security.basic_auth.MySqlConnection")
    @patch("app.infrastructure.security.basic_auth.UserRepository")
    def test_verify_delegates_to_repo(self, mock_repo_cls, mock_conn_cls):
        mock_repo = MagicMock()
        mock_repo.verify_credentials.return_value = "jonnattan"
        mock_repo_cls.return_value = mock_repo
        provider = BasicAuthProvider()
        result = provider.verify("jonnattan", "secret")
        assert result == "jonnattan"
        mock_repo.verify_credentials.assert_called_once_with("jonnattan", "secret")

    @patch("app.infrastructure.security.basic_auth.MySqlConnection")
    @patch("app.infrastructure.security.basic_auth.UserRepository")
    def test_verify_none(self, mock_repo_cls, mock_conn_cls):
        mock_repo = MagicMock()
        mock_repo.verify_credentials.return_value = None
        mock_repo_cls.return_value = mock_repo
        provider = BasicAuthProvider()
        result = provider.verify("bad", "bad")
        assert result is None
