class TestStatusBlueprint:
    def test_status_get(self, client):
        resp = client.get("/status")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"

    def test_status_post(self, client):
        resp = client.post("/status")
        assert resp.status_code == 200

    def test_status_put(self, client):
        resp = client.put("/status")
        assert resp.status_code == 200
