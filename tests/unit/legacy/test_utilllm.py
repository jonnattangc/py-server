import pytest
from unittest.mock import patch, MagicMock

from app.legacy.utilllm import UtilLlm


class TestUtilLlm:
    @patch.dict("os.environ", {
        "LLM_API_KEY": "llm_key",
        "LLM_AES_KEY": "aes",
        "LLM_URL": "https://llm.example.com",
        "LLM_NAME": "model",
        "LLM_MODEL": "v1"
    })
    @patch("app.legacy.utilllm.requests.post")
    def test_send_question_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"result": "Respuesta"})
        llm = UtilLlm()
        result = llm.sendQuestion("¿Cuál es la capital de Chile?")
        assert result == "Respuesta"

    @patch.dict("os.environ", {
        "LLM_API_KEY": "llm_key",
        "LLM_AES_KEY": "aes",
        "LLM_URL": "https://llm.example.com",
        "LLM_NAME": "model",
        "LLM_MODEL": "v1"
    })
    @patch("app.legacy.utilllm.requests.post")
    def test_send_question_failure(self, mock_post):
        mock_post.return_value = MagicMock(status_code=500, json=lambda: {})
        llm = UtilLlm()
        result = llm.sendQuestion("Hola")
        assert result == "No tengo esa respuesta"
