import pytest
from unittest.mock import patch, MagicMock


class TestMainBlueprint:
    def test_index_redirects(self, client):
        resp = client.get("/")
        assert resp.status_code == 302
        assert "/apidocs" in resp.location

    def test_catch_all_redirects(self, client):
        resp = client.get("/somepath")
        assert resp.status_code == 302

    def test_infojonna(self, client):
        resp = client.get("/infojonna")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["Servidor"] == "dev.jonnattan.com"

    def test_favicon(self, client):
        resp = client.get("/favicon.ico")
        assert resp.status_code == 200

    def test_terms(self, client):
        resp = client.get("/terms")
        assert resp.status_code == 200

    def test_privacity(self, client):
        resp = client.get("/privacity")
        assert resp.status_code == 200

    def test_mobile_privacidad(self, client):
        resp = client.get("/mobile/privacidad")
        assert resp.status_code == 200

    def test_mobile_delete(self, client):
        resp = client.get("/mobile/delete")
        assert resp.status_code == 200
        assert b"jonnattan@gmail.com" in resp.data

    def test_mobile_deleted(self, client):
        resp = client.get("/mobile/deleted")
        assert resp.status_code == 200

    def test_mobile_sms(self, client):
        with patch("app.api.routes.main.requests.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200)
            resp = client.post("/mobile/sms", json={"phone": "123"})
            assert resp.status_code == 200
            assert resp.get_json()["code"] == "OK"

    def test_mobile_sms_no_env(self, client):
        with patch.dict("os.environ", {"NOTIFICATION_URL": "", "NOTIFICATION_API_KEY": ""}, clear=False):
            resp = client.post("/mobile/sms", json={"phone": "123"})
            assert resp.status_code == 500

    def test_mobile_validate(self, client):
        resp = client.get("/mobile/validate")
        assert resp.status_code == 200
        assert resp.get_json()["nombre"] == "Jonnattan"

    def test_mobile_door(self, client):
        resp = client.post("/mobile/door", json={"state": True})
        assert resp.status_code == 200
        assert resp.get_json()["opened"] is False

    def test_mobile_sms_subpath(self, client):
        resp = client.post("/mobile/sms", json={"msg": "hi"})
        assert resp.status_code == 200
        assert resp.get_json()["code"] == "OK"
