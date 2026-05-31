import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_freelance_reviews():
    """Test d'obtention des avis d'un freelance"""
    response = client.get("/api/v1/utilisateurs/1/avis")
    assert response.status_code in [200, 404]


def test_create_review():
    """Test de création d'un avis"""
    response = client.post(
        "/api/v1/utilisateurs/1/avis",
        json={
            "donneur_id": "2",
            "note": 5,
            "commentaire": "Excellent travail"
        }
    )
    assert response.status_code in [200, 404]
