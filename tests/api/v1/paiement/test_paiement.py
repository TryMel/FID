import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_subscription_status():
    """Test d'obtention du statut d'abonnement"""
    response = client.get("/api/v1/paiements/statut-abonnement")
    assert response.status_code in [200]


def test_calculate_fees():
    """Test de calcul des frais"""
    response = client.post(
        "/api/v1/paiements/calculer-les-frais",
        json={"montant": 100.0}
    )
    assert response.status_code in [200]
