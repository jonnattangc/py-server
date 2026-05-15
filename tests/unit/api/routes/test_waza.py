from unittest.mock import patch, MagicMock


class TestWazaBlueprint:
    def test_waza_get(self, client):
        with patch("app.api.routes.waza.UtilWaza") as mock_waza:
            mock_inst = MagicMock()
            mock_inst.requestProcess.return_value = ({"msg": "waza"}, 200)
            mock_waza.return_value = mock_inst
            resp = client.get("/waza")
            assert resp.status_code == 200

    def test_waza_subpath(self, client):
        with patch("app.api.routes.waza.UtilWaza") as mock_waza:
            mock_inst = MagicMock()
            mock_inst.requestProcess.return_value = ({"msg": "waza2"}, 200)
            mock_waza.return_value = mock_inst
            resp = client.get("/waza/generate")
            assert resp.status_code == 200
