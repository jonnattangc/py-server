import pytest
from unittest.mock import patch, MagicMock

from app.legacy.memorize import Memorize


class TestMemorize:
    @patch("app.legacy.memorize.pymysql.connect")
    def test_get_states(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"state": "down", "name_state": "card1"},
            {"state": "up", "name_state": "card2"},
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        memo = Memorize()
        names, states = memo.get_states()
        assert names == ["card1", "card2"]
        assert states == ["down", "up"]

    @patch("app.legacy.memorize.pymysql.connect")
    def test_reset(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        memo = Memorize()
        msg, code = memo.reset()
        assert code == 200
        assert "exitosamente" in msg

    @patch("app.legacy.memorize.pymysql.connect")
    def test_process(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        memo = Memorize()
        visible, code = memo.process({"card": "card1", "state": "up"})
        assert code == 200
        assert visible is True

    @patch("app.legacy.memorize.pymysql.connect")
    def test_save_process_down(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        memo = Memorize()
        visible, code = memo.save_process("card1", "down")
        assert visible is False
        assert code == 200
