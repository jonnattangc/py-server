from unittest.mock import patch, MagicMock


class TestLogiaBlueprint:
    def test_logia_post(self, client):
        with patch("app.api.routes.logia.GranLogia") as mock_logia:
            mock_inst = MagicMock()
            mock_inst.request_process.return_value = ({"msg": "logia"}, 200)
            mock_logia.return_value = mock_inst
            resp = client.post("/logia/usergl/login")
            assert resp.status_code == 200
