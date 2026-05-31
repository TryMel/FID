import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_public_profile():
    """Test d'obtention du profil public d'un utilisateur"""
    response = client.get("/api/v1/utilisateurs/1/profile")
    assert response.status_code in [200, 404]


def test_update_profile():
    """Test de mise à jour du profil"""
    response = client.patch(
        "/api/v1/utilisateurs/me/profile",
        json={
            "titre_professionnel": "Développeur Python",
            "biographie": "Expert en développement backend"
        }
    )
    assert response.status_code in [200, 404]
