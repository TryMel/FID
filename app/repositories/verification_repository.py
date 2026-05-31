from sqlalchemy.orm import Session
from app.models import Verification
from typing import Optional, List


class VerificationRepository:
    """Repository pour les vérifications - gère l'accès aux données de vérifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_id_utilisateur(self, user_id: str) -> List[Verification]:
        """Récupérer toutes les vérifications d'un utilisateur"""
        return self.db.query(Verification).filter(Verification.utilisateur_id == user_id).all()
    
    def obtenir_par_id(self, verification_id: str) -> Optional[Verification]:
        """Récupérer une vérification par son ID"""
        return self.db.query(Verification).filter(Verification.id == verification_id).first()
    
    def obtenir_par_code(self, code: str) -> Optional[Verification]:
        """Récupérer une vérification par son code"""
        return self.db.query(Verification).filter(Verification.code == code).first()
    
    def creer(self, verification: Verification) -> Verification:
        """Créer une nouvelle vérification"""
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        return verification
    
    def mettre_a_jour_statut(self, verification_id: str, statut: str) -> Optional[Verification]:
        """Mettre à jour le statut d'une vérification"""
        verification = self.obtenir_par_id(verification_id)
        if verification:
            verification.statut = statut
            self.db.commit()
            self.db.refresh(verification)
        return verification
