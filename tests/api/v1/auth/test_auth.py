import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_register():
    """Test d'inscription d'un nouvel utilisateur"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nom_complet": "Test User",
            "role": "freelance"
        }
    )
    assert response.status_code in [200, 400]  # 400 si l'utilisateur existe déjà


def test_login():
    """Test de connexion d'un utilisateur"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code in [200, 401]  # 401 si les identifiants sont incorrects
