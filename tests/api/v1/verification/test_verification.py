git push -u origin mainimport pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_request_verification():
    """Test de demande de vérification"""
    response = client.post(
        "/api/v1/verification/requête",
        json={"type": "identité"}
    )
    assert response.status_code in [200]


def test_get_verification_status():
    """Test d'obtention du statut de vérification"""
    response = client.get("/api/v1/verification/statut")
    assert response.status_code in [200]
