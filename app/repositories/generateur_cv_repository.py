from sqlalchemy.orm import Session
from app.models import CV
from typing import Optional


class GenerateurCVRepository:
    """Repository pour les CV - gère l'accès aux données de CV"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_id_utilisateur(self, user_id: str) -> Optional[CV]:
        """Récupérer le CV d'un utilisateur"""
        return self.db.query(CV).filter(CV.utilisateur_id == user_id).first()
    
    def obtenir_par_id(self, cv_id: str) -> Optional[CV]:
        """Récupérer un CV par son ID"""
        return self.db.query(CV).filter(CV.id == cv_id).first()
    
    def creer(self, cv: CV) -> CV:
        """Créer un nouveau CV"""
        self.db.add(cv)
        self.db.commit()
        self.db.refresh(cv)
        return cv
    
    def mettre_a_jour(self, cv: CV) -> CV:
        """Mettre à jour un CV"""
        self.db.commit()
        self.db.refresh(cv)
        return cv
