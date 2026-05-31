import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_my_score():
    """Test d'obtention de mon score de confiance"""
    response = client.get("/api/v1/score-confiance/moi")
    assert response.status_code in [200, 404]


def test_get_user_score():
    """Test d'obtention du score d'un utilisateur"""
    response = client.get("/api/v1/score-confiance/1")
    assert response.status_code in [200]
