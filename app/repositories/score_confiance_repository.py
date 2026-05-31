from sqlalchemy.orm import Session
from app.models import ScoreConfiance
from typing import Optional


class ScoreConfianceRepository:
    """Repository pour les scores de confiance - gère l'accès aux données de scores"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_id_utilisateur(self, user_id: str) -> Optional[ScoreConfiance]:
        """Récupérer le score de confiance d'un utilisateur"""
        return self.db.query(ScoreConfiance).filter(ScoreConfiance.utilisateur_id == user_id).first()
    
    def creer(self, score: ScoreConfiance) -> ScoreConfiance:
        """Créer un nouveau score de confiance"""
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score
    
    def mettre_a_jour(self, score: ScoreConfiance) -> ScoreConfiance:
        """Mettre à jour un score de confiance"""
        self.db.commit()
        self.db.refresh(score)
        return score
