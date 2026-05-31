from sqlalchemy.orm import Session
from app.models import ValidationSociale
from app.repositories.validation_sociale_repository import ValidationSocialeRepository
from typing import Optional, List
import re

class ValidationSocialeService:
    def __init__(self, db: Session):
        self.db = db
        self.validation_repo = ValidationSocialeRepository(db)

    def valider_lien_social(self, utilisateur_id: str, plateforme: str, url: str, country: str = "CI") -> ValidationSociale:
        """Valider un lien social"""
        # Vérifier si le domaine est autorisé
        if not self.est_domaine_autorise(plateforme, url, country):
            raise ValueError(f"Le domaine {plateforme} n'est pas autorisé")
        
        # Vérifier le format de l'URL
        if not self.est_url_valide(url):
            raise ValueError("L'URL doit commencer par https://")
        
        validation = ValidationSociale(
            utilisateur_id=utilisateur_id,
            plateforme=plateforme,
            url=url,
            statut="valide"
        )
        
        return self.validation_repo.creer(validation)

    def obtenir_domaines_autorises(self, country: str = "CI") -> List[str]:
        """Obtenir les domaines autorisés selon le pays"""
        return self.validation_repo.obtenir_domaines_autorises(country)

    def est_domaine_autorise(self, plateforme: str, url: str, country: str) -> bool:
        """Vérifier si le domaine est autorisé"""
        allowed_domains = self.obtenir_domaines_autorises(country)
        
        for domain in allowed_domains:
            if domain in url.lower():
                return True
        
        return False

    def est_url_valide(self, url: str) -> bool:
        """Vérifier si l'URL est valide"""
        return url.startswith("https://")

    def obtenir_validations_utilisateur(self, utilisateur_id: str) -> List[ValidationSociale]:
        """Obtenir les validations sociales d'un utilisateur"""
        return self.validation_repo.obtenir_par_id_utilisateur(utilisateur_id)

    def verifier_quota_liens_sociaux(self, utilisateur_id: str, palier: str) -> bool:
        """Vérifier si l'utilisateur peut ajouter des liens sociaux selon son palier"""
        validations = self.obtenir_validations_utilisateur(utilisateur_id)
        quotas = {
            "gratuit": 1,
            "pro": 5,
            "premium": 999  # Illimité
        }
        return len(validations) < quotas.get(palier, 1)
