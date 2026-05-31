from sqlalchemy.orm import Session
from app.models import Paiement
from typing import Optional, List


class PaiementRepository:
    """Repository pour les paiements - gère l'accès aux données de paiements"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_id_utilisateur(self, user_id: str) -> List[Paiement]:
        """Récupérer tous les paiements d'un utilisateur"""
        return self.db.query(Paiement).filter(Paiement.utilisateur_id == user_id).all()
    
    def obtenir_par_id(self, paiement_id: str) -> Optional[Paiement]:
        """Récupérer un paiement par son ID"""
        return self.db.query(Paiement).filter(Paiement.id == paiement_id).first()
    
    def creer(self, paiement: Paiement) -> Paiement:
        """Créer un nouveau paiement"""
        self.db.add(paiement)
        self.db.commit()
        self.db.refresh(paiement)
        return paiement
    
    def mettre_a_jour_statut(self, paiement_id: str, statut: str) -> Optional[Paiement]:
        """Mettre à jour le statut d'un paiement"""
        paiement = self.obtenir_par_id(paiement_id)
        if paiement:
            paiement.statut = statut
            self.db.commit()
            self.db.refresh(paiement)
        return paiement
