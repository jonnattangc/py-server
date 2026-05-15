import pytest
from unittest.mock import patch, MagicMock
import imaplib

from app.legacy.utilmail import MailProcess


class TestMailProcess:
    def test_init(self):
        mp = MailProcess()
        assert mp.root is not None

    def test_request_process_read(self):
        mp = MailProcess()
        with patch.object(mp, "read", return_value={"status": "Ok"}) as mock_read:
            data, code = mp.request_process(MagicMock(), "read")
            assert code == 200
            assert data["status"] == "Ok"
            mock_read.assert_called_once()

    @patch("app.legacy.utilmail.imaplib.IMAP4_SSL")
    def test_read(self, mock_imap_cls):
        mock_mail = MagicMock()
        mock_mail.search.return_value = ("OK", [b"1 2"])
        mock_mail.fetch.return_value = ("OK", [(b"1", b"Subject: test")])
        mock_imap_cls.return_value = mock_mail

        mp = MailProcess()
        result = mp.read()
        assert "status" in result
