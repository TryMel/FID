import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_validate_social():
    """Test de validation de lien social"""
    response = client.post(
        "/api/v1/validation-sociale/valider",
        json={"plateforme": "linkedin", "url": "https://linkedin.com/in/test"}
    )
    assert response.status_code in [200]


def test_get_allowed_domains():
    """Test d'obtention des domaines autorisés"""
    response = client.get("/api/v1/validation-sociale/domaines-autorises")
    assert response.status_code in [200]
