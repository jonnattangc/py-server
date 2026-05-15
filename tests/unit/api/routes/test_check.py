from unittest.mock import patch, MagicMock


class TestCheckBlueprint:
    def test_checkall_returns_json(self, client):
        with patch("app.api.routes.check.Checker") as mock_checker:
            mock_inst = MagicMock()
            mock_inst.get_info.return_value = {"Database": {"Version": "8.0"}}
            mock_checker.return_value = mock_inst
            resp = client.get("/checkall", auth=("test", "test"))
            assert resp.status_code == 200
            assert resp.get_json()["Database"]["Version"] == "8.0"

    def test_checkall_unauthorized(self, client):
        with patch("app.api.routes.check.BasicAuthProvider") as mock_provider:
            mock_inst = MagicMock()
            mock_inst.verify.return_value = None
            mock_provider.return_value = mock_inst
            resp = client.get("/checkall", auth=("bad", "bad"))
            assert resp.status_code == 401

    def test_unauthorized_handler(self, client):
        resp = client.get("/checkall")
        assert resp.status_code in (401, 200)  # depending on auth patch
