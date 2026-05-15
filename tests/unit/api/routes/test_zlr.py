from unittest.mock import patch, MagicMock


class TestZlrBlueprint:
    def test_zlr_get(self, client):
        with patch("app.api.routes.zlr.Irelez") as mock_zlr:
            mock_inst = MagicMock()
            mock_inst.request_process.return_value = ({"data": "zlr"}, 200)
            mock_zlr.return_value = mock_inst
            resp = client.get("/zlr/test")
            assert resp.status_code == 200
            assert resp.get_json()["data"] == "zlr"
