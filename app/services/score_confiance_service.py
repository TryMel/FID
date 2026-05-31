from sqlalchemy.orm import Session
from app.models import ScoreConfiance, Avis, Collaboration
from app.repositories.score_confiance_repository import ScoreConfianceRepository
from app.repositories.avis_repository import AvisRepository
from app.repositories.collaboration_repository import CollaborationRepository
from typing import Optional

class ScoreConfianceService:
    def __init__(self, db: Session):
        self.db = db
        self.score_repo = ScoreConfianceRepository(db)
        self.avis_repo = AvisRepository(db)
        self.collaboration_repo = CollaborationRepository(db)

    def obtenir_mon_score(self, utilisateur_id: str) -> Optional[ScoreConfiance]:
        """Obtenir mon score de confiance"""
        return self.score_repo.obtenir_par_id_utilisateur(utilisateur_id)

    def mettre_a_jour_score(self, utilisateur_id: str) -> ScoreConfiance:
        """Mettre à jour le score de confiance d'un utilisateur"""
        score = self.obtenir_mon_score(utilisateur_id)
        
        if not score:
            score = ScoreConfiance(utilisateur_id=utilisateur_id)
            score = self.score_repo.creer(score)
        
        # Calcul du score basé sur plusieurs facteurs
        avis_recus = self.avis_repo.obtenir_par_id_freelance(utilisateur_id)
        nombre_avis = len(avis_recus)
        
        collaborations = self.collaboration_repo.obtenir_toutes()
        nombre_projets = len([c for c in collaborations if c.freelance_id == utilisateur_id and c.statut == "termine"])
        
        # Calcul de la note moyenne
        note_moyenne = sum(a.note for a in avis_recus) / len(avis_recus) if avis_recus else 0
        
        # Calcul du score (0-100)
        score_calcul = min(100, (note_moyenne * 20) + (nombre_avis * 2) + (nombre_projets * 3))
        
        score.score = round(score_calcul)
        score.nombre_avis = nombre_avis
        score.nombre_projets = nombre_projets
        
        return self.score_repo.mettre_a_jour(score)

    def obtenir_score_utilisateur(self, utilisateur_id: str, palier: str = "gratuit") -> dict:
        """Obtenir le score de confiance d'un utilisateur (public)"""
        score = self.obtenir_mon_score(utilisateur_id)
        
        if not score:
            return {
                "score": 0,
                "niveau": "Faible",
                "visible": False
            }
        
        # Visibilité selon le palier
        visible = palier in ["pro", "premium"]
        
        niveau = self.obtenir_niveau_score(score.score)
        
        return {
            "score": score.score if visible else None,
            "niveau": niveau if visible else None,
            "visible": visible
        }

    def obtenir_niveau_score(self, score: float) -> str:
        """Obtenir le niveau de confiance"""
        if score >= 80:
            return "Premium"
        elif score >= 60:
            return "Élevé"
        elif score >= 40:
            return "Moyen"
        else:
            return "Faible"
