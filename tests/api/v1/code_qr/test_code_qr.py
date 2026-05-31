import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_generate_qr_code():
    """Test de génération de code QR"""
    response = client.post("/api/v1/code-qr/generer")
    assert response.status_code in [200]


def test_get_my_qr_code():
    """Test d'obtention de mon code QR"""
    response = client.get("/api/v1/code-qr/moi")
    assert response.status_code in [200]
