from unittest.mock import patch, MagicMock


class TestMailBlueprint:
    def test_mail_read(self, client):
        with patch("app.api.routes.mail.MailProcess") as mock_mail:
            mock_inst = MagicMock()
            mock_inst.request_process.return_value = ({"status": "Ok"}, 200)
            mock_mail.return_value = mock_inst
            resp = client.get("/mail/read")
            assert resp.status_code == 200
            assert resp.get_json()["status"] == "Ok"
