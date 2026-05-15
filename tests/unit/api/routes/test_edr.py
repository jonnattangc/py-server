from unittest.mock import patch, MagicMock


class TestEdrBlueprint:
    def test_edr_post(self, client):
        with patch("app.api.routes.edr.Dernede") as mock_edr:
            mock_inst = MagicMock()
            mock_inst.requestProcess.return_value = ({"data": "x"}, 200)
            mock_edr.return_value = mock_inst
            resp = client.post("/edr/action", auth=("u", "p"))
            assert resp.status_code == 200
            assert resp.get_json()["data"] == "x"
