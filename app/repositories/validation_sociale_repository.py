from sqlalchemy.orm import Session
from app.models import ValidationSociale
from typing import List


class ValidationSocialeRepository:
    """Repository pour les validations sociales - gère l'accès aux données de validations sociales"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_id_utilisateur(self, user_id: str) -> List[ValidationSociale]:
        """Récupérer toutes les validations sociales d'un utilisateur"""
        return self.db.query(ValidationSociale).filter(ValidationSociale.utilisateur_id == user_id).all()
    
    def creer(self, validation: ValidationSociale) -> ValidationSociale:
        """Créer une nouvelle validation sociale"""
        self.db.add(validation)
        self.db.commit()
        self.db.refresh(validation)
        return validation
    
    def obtenir_domaines_autorises(self, country: str) -> List[str]:
        """Récupérer les domaines autorisés pour un pays"""
        # Cette méthode pourrait être étendue pour récupérer depuis une table de configuration
        domains = {
            "CI": ["linkedin.com", "twitter.com", "facebook.com", "instagram.com"],
            "FR": ["linkedin.com", "twitter.com", "facebook.com", "instagram.com", "viadeo.com"],
            "US": ["linkedin.com", "twitter.com", "facebook.com", "instagram.com", "github.com"]
        }
        return domains.get(country, ["linkedin.com", "twitter.com"])
