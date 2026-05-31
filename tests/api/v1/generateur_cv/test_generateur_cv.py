import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_generate_cv():
    """Test de génération de CV"""
    response = client.post(
        "/api/v1/generateur-cv/generer",
        json={"template_id": "template1", "langue": "fr"}
    )
    assert response.status_code in [200]


def test_get_templates():
    """Test d'obtention des templates de CV"""
    response = client.get("/api/v1/generateur-cv/modeles")
    assert response.status_code in [200]
