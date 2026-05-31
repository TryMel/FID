from sqlalchemy.orm import Session
from app.models import Profil, Experience, Competence
from typing import Optional, List


class ProfilRepository:
    """Repository pour les profils - gère l'accès aux données de profil"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_id_utilisateur(self, user_id: str) -> Optional[Profil]:
        """Récupérer le profil d'un utilisateur"""
        return self.db.query(Profil).filter(Profil.utilisateur_id == user_id).first()
    
    def creer(self, profil: Profil) -> Profil:
        """Créer un nouveau profil"""
        self.db.add(profil)
        self.db.commit()
        self.db.refresh(profil)
        return profil
    
    def mettre_a_jour(self, profil: Profil) -> Profil:
        """Mettre à jour un profil"""
        self.db.commit()
        self.db.refresh(profil)
        return profil
    
    def obtenir_experiences(self, user_id: str) -> List[Experience]:
        """Récupérer les expériences d'un utilisateur"""
        return self.db.query(Experience).filter(Experience.utilisateur_id == user_id).all()
    
    def creer_experience(self, experience: Experience) -> Experience:
        """Créer une nouvelle expérience"""
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        return experience
    
    def obtenir_competences(self, user_id: str) -> List[Competence]:
        """Récupérer les compétences d'un utilisateur"""
        return self.db.query(Competence).filter(Competence.utilisateur_id == user_id).all()
    
    def creer_competence(self, competence: Competence) -> Competence:
        """Créer une nouvelle compétence"""
        self.db.add(competence)
        self.db.commit()
        self.db.refresh(competence)
        return competence
