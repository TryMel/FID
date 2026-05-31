import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_collaborations():
    """Test d'obtention de toutes les collaborations"""
    response = client.get("/api/v1/collaborations/")
    assert response.status_code in [200]


def test_create_collaboration():
    """Test de création d'une collaboration"""
    response = client.post(
        "/api/v1/collaborations/",
        json={
            "client_id": "1",
            "freelance_id": "2",
            "titre": "Projet web",
            "description": "Développement d'un site web",
            "budget": 1000.0
        }
    )
    assert response.status_code in [200, 404]
