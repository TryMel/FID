from sqlalchemy.orm import Session
from app.models import Utilisateur
from typing import Optional


class AuthRepository:
    """Repository pour l'authentification - gère l'accès aux données utilisateur"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_email(self, email: str) -> Optional[Utilisateur]:
        """Récupérer un utilisateur par son email"""
        return self.db.query(Utilisateur).filter(Utilisateur.email == email).first()
    
    def obtenir_par_id(self, user_id: str) -> Optional[Utilisateur]:
        """Récupérer un utilisateur par son ID"""
        return self.db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    def creer(self, utilisateur: Utilisateur) -> Utilisateur:
        """Créer un nouvel utilisateur"""
        self.db.add(utilisateur)
        self.db.commit()
        self.db.refresh(utilisateur)
        return utilisateur
    
    def mettre_a_jour(self, utilisateur: Utilisateur) -> Utilisateur:
        """Mettre à jour un utilisateur"""
        self.db.commit()
        self.db.refresh(utilisateur)
        return utilisateur
