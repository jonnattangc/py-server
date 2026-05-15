from unittest.mock import patch, MagicMock


class TestCryptoBlueprint:
    def test_cmkt_get(self, client):
        with patch("app.api.routes.crypto.Coordinator") as mock_coord:
            mock_inst = MagicMock()
            mock_inst.proccess_solicitude.return_value = ({"status": "ok"}, 200)
            mock_coord.return_value = mock_inst
            resp = client.get("/cmkt/test", auth=("u", "p"))
            assert resp.status_code == 200
            assert resp.get_json()["status"] == "ok"
