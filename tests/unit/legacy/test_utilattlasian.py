import pytest
from unittest.mock import patch, MagicMock

from app.legacy.utilattlasian import UtilAttlasian


class TestUtilAttlasian:
    @patch("app.legacy.utilattlasian.pymysql.connect")
    def test_init(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        util = UtilAttlasian()
        assert util.db is not None

    @patch("app.legacy.utilattlasian.pymysql.connect")
    def test_save_msgs(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        util = UtilAttlasian()
        util.saveMsgs("rx", "tx", "user", "+569")
        mock_conn.commit.assert_called()

    @patch("app.legacy.utilattlasian.pymysql.connect")
    def test_request_process_no_path(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        util = UtilAttlasian()
        req = MagicMock()
        req.method = "GET"
        req.headers = {}
        req.data = b""
        req.get_json.return_value = {}
        data, code = util.requestProcess(req, None)
        assert code == 404
