from unittest.mock import patch, MagicMock


class TestDreamsBlueprint:
    def test_dreams_post(self, client):
        with patch("app.api.routes.dreams.Coordinator") as mock_coord:
            mock_inst = MagicMock()
            mock_inst.proccess_solicitude.return_value = ({"msg": "dream"}, 200)
            mock_coord.return_value = mock_inst
            resp = client.post("/dreams/deposito", auth=("u", "p"))
            assert resp.status_code == 200
            assert resp.get_json()["msg"] == "dream"
