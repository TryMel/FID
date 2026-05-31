import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_user_statistics():
    """Test d'obtention des statistiques d'un utilisateur"""
    response = client.get("/api/v1/utilisateurs/1/statistiques")
    assert response.status_code in [200]
