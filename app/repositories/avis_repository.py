"""
Repository Avis
================
Couche d'accès aux données pour les avis clients.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Avis
from typing import List, Optional


class AvisRepository:
    """Repository pour les avis"""

    def __init__(self, db: Session):
        self.db = db

    def obtenir_par_id_freelance(self, freelance_id: str) -> List[Avis]:
        """Récupérer tous les avis d'un freelance (sans pagination)"""
        return (
            self.db.query(Avis)
            .filter(Avis.receveur_id == freelance_id)
            .order_by(Avis.date_creation.desc())
            .all()
        )

    def obtenir_par_id_freelance_pagine(
        self, freelance_id: str, page: int = 1, limite: int = 10
    ) -> List[Avis]:
        """Récupérer les avis d'un freelance avec pagination"""
        decalage = (page - 1) * limite
        return (
            self.db.query(Avis)
            .filter(Avis.receveur_id == freelance_id)
            .order_by(Avis.date_creation.desc())
            .offset(decalage)
            .limit(limite)
            .all()
        )

    def compter_par_freelance(self, freelance_id: str) -> int:
        """Compter le nombre total d'avis d'un freelance"""
        return (
            self.db.query(func.count(Avis.id))
            .filter(Avis.receveur_id == freelance_id)
            .scalar() or 0
        )

    def note_moyenne_freelance(self, freelance_id: str) -> Optional[float]:
        """Calculer la note moyenne d'un freelance"""
        return (
            self.db.query(func.avg(Avis.note))
            .filter(Avis.receveur_id == freelance_id)
            .scalar()
        )

    def creer(self, avis: Avis) -> Avis:
        """Créer un nouvel avis"""
        self.db.add(avis)
        self.db.commit()
        self.db.refresh(avis)
        return avis
