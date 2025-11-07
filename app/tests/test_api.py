from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_analizar_mock_http():
    r = client.post("/analizar-mock", json={"url": "http://example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["info_enlace"]["es_seguro_httpsO"] is False
