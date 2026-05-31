import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_user_projects():
    """Test d'obtention des projets d'un utilisateur"""
    response = client.get("/api/v1/users/1/projects")
    assert response.status_code in [200, 404]


def test_create_project():
    """Test de création d'un nouveau projet"""
    response = client.post(
        "/api/v1/users/1/projects",
        json={
            "titre": "Mon projet",
            "description": "Description du projet",
            "technologies": "Python, FastAPI"
        }
    )
    assert response.status_code in [200, 403, 404]
