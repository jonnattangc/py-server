from unittest.mock import patch, MagicMock


class TestCxpBlueprint:
    def test_cxp_get(self, client):
        with patch("app.api.routes.cxp.Sserpxelihc") as mock_cxp:
            mock_inst = MagicMock()
            mock_inst.requestProcess.return_value = ({"data": "cxp"}, 200)
            mock_cxp.return_value = mock_inst
            resp = client.get("/cxp/rating/test")
            assert resp.status_code == 200
            assert resp.get_json()["data"] == "cxp"
