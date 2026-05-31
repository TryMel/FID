"""
Repository Collaboration
=========================
Couche d'accès aux données pour les missions/collaborations.
Pas de logique métier ici — uniquement des opérations SQL.
"""
from sqlalchemy.orm import Session
from app.models import Collaboration
from typing import Optional, List


class CollaborationRepository:
    """Repository pour les collaborations"""

    def __init__(self, db: Session):
        self.db = db

    def obtenir_toutes(self) -> List[Collaboration]:
        """Récupérer toutes les collaborations"""
        return self.db.query(Collaboration).all()

    def obtenir_par_id(self, collaboration_id: str) -> Optional[Collaboration]:
        """Récupérer une collaboration par son ID"""
        return self.db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()

    def obtenir_par_client(self, client_id: str) -> List[Collaboration]:
        """Récupérer toutes les missions publiées par un client"""
        return (
            self.db.query(Collaboration)
            .filter(Collaboration.client_id == client_id)
            .order_by(Collaboration.date_creation.desc())
            .all()
        )

    def obtenir_par_freelance(self, freelance_id: str) -> List[Collaboration]:
        """Récupérer toutes les missions assignées à un freelance"""
        return (
            self.db.query(Collaboration)
            .filter(Collaboration.freelance_id == freelance_id)
            .order_by(Collaboration.date_creation.desc())
            .all()
        )

    def creer(self, collaboration: Collaboration) -> Collaboration:
        """Créer une nouvelle collaboration"""
        self.db.add(collaboration)
        self.db.commit()
        self.db.refresh(collaboration)
        return collaboration

    def mettre_a_jour_statut(self, collaboration_id: str, statut: str) -> Optional[Collaboration]:
        """Mettre à jour le statut d'une collaboration"""
        collaboration = self.obtenir_par_id(collaboration_id)
        if collaboration:
            collaboration.statut = statut
            self.db.commit()
            self.db.refresh(collaboration)
        return collaboration
