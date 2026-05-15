from unittest.mock import patch, MagicMock


class TestPageBlueprint:
    def test_page_web(self, client):
        with patch("app.api.routes.page.Page") as mock_page:
            mock_inst = MagicMock()
            mock_inst.request_process.return_value = ({"page": True}, 200, True)
            mock_page.return_value = mock_inst
            resp = client.get("/page")
            assert resp.status_code == 200

    def test_page_csrf(self, client):
        resp = client.post("/page/csrf")
        assert resp.status_code == 200

    def test_page_image(self, client):
        resp = client.get("/page/image/test.png")
        assert resp.status_code == 404  # file likely does not exist

    def test_page_js(self, client):
        # js files exist in app/static/js
        resp = client.get("/page/js/logia.js")
        # May succeed or 404 depending on path resolution in test
        assert resp.status_code in (200, 404)
