from unittest.mock import patch, MagicMock


class TestUccBlueprint:
    def test_ucc_post(self, client):
        with patch("app.api.routes.ucc.Ucc") as mock_ucc:
            mock_inst = MagicMock()
            mock_inst.request_process.return_value = ({"msg": "ucc"}, 200)
            mock_ucc.return_value = mock_inst
            resp = client.post("/ucc/sign", auth=("u", "p"))
            assert resp.status_code == 200

    def test_ucc_get(self, client):
        with patch("app.api.routes.ucc.Ucc") as mock_ucc:
            mock_inst = MagicMock()
            mock_inst.request_process.return_value = ({"msg": "ucc"}, 200)
            mock_ucc.return_value = mock_inst
            resp = client.get("/ucc/sign", auth=("u", "p"))
            assert resp.status_code == 200
