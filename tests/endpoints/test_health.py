"""Root (/) and health (/health) endpoints — no auth required."""


class TestRootEndpoint:
    def test_returns_welcome_message(self, http_client):
        res = http_client.get("/")
        assert res.status_code == 200
        assert res.json() == {"message": "Tailor Backend Running"}


class TestHealthEndpoint:
    def test_returns_status_key(self, http_client):
        res = http_client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] in ("healthy", "degraded")

    def test_reports_api_operational(self, http_client):
        body = http_client.get("/health").json()
        assert body["services"]["api"] == "operational"

    def test_includes_version_and_environment(self, http_client):
        body = http_client.get("/health").json()
        assert "version" in body
        assert "environment" in body
