from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_documentacion_disponible():
    """La app levanta y expone Swagger (/docs)."""
    assert client.get("/docs").status_code == 200


def test_esquema_openapi_generado():
    """El esquema OpenAPI se genera correctamente."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "Educar para Transformar"