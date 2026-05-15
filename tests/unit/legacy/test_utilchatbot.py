import pytest
from unittest.mock import patch, MagicMock

from app.legacy.utilchatbot import UtilChatbot


class TestUtilChatbot:
    @patch.dict("os.environ", {"CHATBOT_API_KEY": "key123", "FILE_CHAT_KEY": "doc123"})
    @patch("app.legacy.utilchatbot.requests.post")
    def test_send_question_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"content": "Hola"})
        cb = UtilChatbot()
        result = cb.sendQuestion("Hola")
        assert result == "Hola"

    @patch.dict("os.environ", {"CHATBOT_API_KEY": "key123", "FILE_CHAT_KEY": "doc123"})
    @patch("app.legacy.utilchatbot.requests.post")
    def test_send_question_failure(self, mock_post):
        mock_post.return_value = MagicMock(status_code=500, json=lambda: {})
        cb = UtilChatbot()
        result = cb.sendQuestion("Hola")
        assert result == "No tengo esa respuesta"
