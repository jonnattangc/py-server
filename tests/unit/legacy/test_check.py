import pytest
from unittest.mock import patch, MagicMock

from app.legacy.check import Checker


class TestChecker:
    @patch("app.legacy.check.pymysql.connect")
    @patch("app.legacy.check.psutil")
    def test_get_info(self, mock_psutil, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"version": "8.0.30"}]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        mock_mem = MagicMock()
        mock_mem.total = 8 * (1024**3)
        mock_mem.available = 4 * (1024**3)
        mock_mem.used = 4 * (1024**3)
        mock_mem.percent = 50
        mock_psutil.virtual_memory.return_value = mock_mem

        mock_disk = MagicMock()
        mock_disk.total = 100 * (1024**3)
        mock_disk.free = 50 * (1024**3)
        mock_disk.used = 50 * (1024**3)
        mock_disk.percent = 50
        mock_psutil.disk_usage.return_value = mock_disk

        mock_psutil.cpu_count.side_effect = [4, 8]
        mock_psutil.boot_time.return_value = 0

        checker = Checker()
        info = checker.get_info()
        assert "Database" in info
        assert info["Database"]["NAME"] == "MySQL"
        assert "Memoria" in info
        assert "CPU" in info
        assert info["CPU"]["Cores"] == 4

    @patch("app.legacy.check.pymysql.connect")
    def test_is_connect(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"version": "8.0"}]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        checker = Checker()
        version = checker.is_connect()
        assert version == "8.0"

    @patch("app.legacy.check.pymysql.connect", side_effect=Exception("fail"))
    def test_init_failure(self, mock_connect):
        checker = Checker()
        assert checker.db is None
