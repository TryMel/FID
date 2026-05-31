import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_dashboard_stats():
    """Test d'obtention des statistiques du tableau de bord admin"""
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code in [200]


def test_get_all_users():
    """Test d'obtention de tous les utilisateurs"""
    response = client.get("/api/v1/admin/users")
    assert response.status_code in [200]
