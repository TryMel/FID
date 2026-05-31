from sqlalchemy.orm import Session
from app.models import Projet
from typing import Optional, List


class PortfolioRepository:
    """Repository pour les portfolios - gère l'accès aux données de projets"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_id_utilisateur(self, user_id: str) -> List[Projet]:
        """Récupérer tous les projets d'un utilisateur"""
        return self.db.query(Projet).filter(Projet.utilisateur_id == user_id).all()
    
    def obtenir_par_id(self, project_id: str) -> Optional[Projet]:
        """Récupérer un projet par son ID"""
        return self.db.query(Projet).filter(Projet.id == project_id).first()
    
    def creer(self, projet: Projet) -> Projet:
        """Créer un nouveau projet"""
        self.db.add(projet)
        self.db.commit()
        self.db.refresh(projet)
        return projet
    
    def mettre_a_jour(self, projet: Projet) -> Projet:
        """Mettre à jour un projet"""
        self.db.commit()
        self.db.refresh(projet)
        return projet
    
    def supprimer(self, project_id: str) -> bool:
        """Supprimer un projet"""
        projet = self.obtenir_par_id(project_id)
        if projet:
            self.db.delete(projet)
            self.db.commit()
            return True
        return False
    
    def compter_par_id_utilisateur(self, user_id: str) -> int:
        """Compter le nombre de projets d'un utilisateur"""
        return self.db.query(Projet).filter(Projet.utilisateur_id == user_id).count()
