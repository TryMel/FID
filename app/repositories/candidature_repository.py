"""
Repository Candidature
========================
Couche d'accès aux données pour les candidatures (postulations freelance).
Pas de logique métier ici - uniquement des opérations SQL.
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.candidature import Candidature
from typing import Optional, List


class CandidatureRepository:
    """Repository pour les candidatures - gère l'accès aux données de candidatures"""

    def __init__(self, db: Session):
        self.db = db

    def creer(self, candidature: Candidature) -> Candidature:
        """Créer une nouvelle candidature"""
        self.db.add(candidature)
        self.db.commit()
        self.db.refresh(candidature)
        return candidature

    def obtenir_par_id(self, candidature_id: str) -> Optional[Candidature]:
        """Récupérer une candidature par son ID"""
        return self.db.query(Candidature).filter(Candidature.id == candidature_id).first()

    def obtenir_par_collaboration(self, collaboration_id: str) -> List[Candidature]:
        """
        Récupérer toutes les candidatures d'une mission.
        Triées par : 1) prioritaire (boostées en premier), 2) date de création
        → Mimétisme social : le client voit d'abord les candidatures boostées (payantes)
        """
        return (
            self.db.query(Candidature)
            .filter(Candidature.collaboration_id == collaboration_id)
            .order_by(Candidature.prioritaire.desc(), Candidature.date_creation.asc())
            .all()
        )

    def obtenir_par_freelance(self, freelance_id: str) -> List[Candidature]:
        """Récupérer toutes les candidatures d'un freelance"""
        return (
            self.db.query(Candidature)
            .filter(Candidature.freelance_id == freelance_id)
            .all()
        )

    def candidature_existante(self, collaboration_id: str, freelance_id: str) -> bool:
        """Vérifier si un freelance a déjà postulé à cette mission"""
        return (
            self.db.query(Candidature)
            .filter(
                Candidature.collaboration_id == collaboration_id,
                Candidature.freelance_id == freelance_id,
            )
            .first()
        ) is not None

    def compter_par_collaboration(self, collaboration_id: str) -> int:
        """Compter le nombre de candidatures pour une mission (preuve sociale)"""
        return (
            self.db.query(func.count(Candidature.id))
            .filter(Candidature.collaboration_id == collaboration_id)
            .scalar()
        )

    def mettre_a_jour_statut(self, candidature_id: str, statut: str) -> Optional[Candidature]:
        """Mettre à jour le statut d'une candidature"""
        candidature = self.obtenir_par_id(candidature_id)
        if candidature:
            candidature.statut = statut
            self.db.commit()
            self.db.refresh(candidature)
        return candidature

    def activer_boost(self, candidature_id: str) -> Optional[Candidature]:
        """Activer le boost (prioritaire=True) sur une candidature"""
        candidature = self.obtenir_par_id(candidature_id)
        if candidature:
            candidature.prioritaire = True
            self.db.commit()
            self.db.refresh(candidature)
        return candidature

    def mettre_a_jour(self, candidature: Candidature) -> Candidature:
        """Mettre à jour une candidature"""
        self.db.commit()
        self.db.refresh(candidature)
        return candidature
