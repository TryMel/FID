from sqlalchemy.orm import Session
from app.models import Paiement, Utilisateur
from app.repositories.paiement_repository import PaiementRepository
from app.repositories.auth_repository import AuthRepository
from typing import Optional, Dict
from datetime import datetime

class PaiementService:
    def __init__(self, db: Session):
        self.db = db
        self.paiement_repo = PaiementRepository(db)
        self.auth_repo = AuthRepository(db)

    def obtenir_statut_abonnement(self, utilisateur_id: str) -> Dict:
        """Obtenir le statut d'abonnement d'un utilisateur"""
        utilisateur = self.auth_repo.obtenir_par_id(utilisateur_id)
        if not utilisateur:
            raise ValueError("Utilisateur non trouvé")
        
        # Simulation - à remplacer par la vraie logique d'abonnement
        return {
            "statut": "actif",
            "palier": "gratuit",
            "date_expiration": None,
            "devise": "XOF"
        }

    def creer_intention_paiement(self, utilisateur_id: str, montant: float, palier: str, country: str = "CI") -> Dict:
        """Créer une intention de paiement Stripe"""
        # Simulation - à remplacer par l'intégration Stripe réelle
        return {
            "client_secret": f"pi_example_{utilisateur_id}",
            "amount": montant,
            "currency": self.obtenir_devise_pour_pays(country),
            "palier": palier
        }

    def verifier_paiement(self, payment_id: str) -> Dict:
        """Vérifier un paiement"""
        # Simulation - à remplacer par la vérification Stripe réelle
        return {
            "status": "succès",
            "payment_id": payment_id
        }

    def calculer_frais(self, montant: float, country: str = "CI") -> Dict:
        """Calculer les frais avec TVA et conversion devise"""
        # Simulation - à remplacer par le calcul réel selon le pays
        taux_tva = self.obtenir_taux_tva_pour_pays(country)
        tva = montant * taux_tva
        total = montant + tva
        
        return {
            "montant_base": montant,
            "tva": tva,
            "taux_tva": taux_tva,
            "total": total,
            "devise": self.obtenir_devise_pour_pays(country)
        }

    def obtenir_devise_pour_pays(self, country: str) -> str:
        """Obtenir la devise pour un pays donné"""
        currency_map = {
            "CI": "XOF",
            "FR": "EUR",
            "US": "USD",
            "NG": "NGN",
            "KE": "KES"
        }
        return currency_map.get(country, "USD")

    def obtenir_taux_tva_pour_pays(self, country: str) -> float:
        """Obtenir le taux de TVA pour un pays donné"""
        vat_map = {
            "CI": 0.18,  # 18% TVA en Côte d'Ivoire
            "FR": 0.20,  # 20% TVA en France
            "US": 0.00,  # Pas de TVA aux US
            "NG": 0.05,  # 5% TVA au Nigeria
            "KE": 0.16   # 16% TVA au Kenya
        }
        return vat_map.get(country, 0.00)
