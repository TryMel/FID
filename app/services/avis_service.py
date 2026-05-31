"""
Service Avis
=============
Logique métier pour les avis clients sur les freelances.

ACTEURS CONCERNÉS :
- CLIENT PARTICULIER / ENTREPRISE : laisse un avis après collaboration terminée
- FREELANCE / PUBLIC : consulte les avis en lecture seule

RÈGLES MÉTIER :
- Un avis ne peut être laissé que sur une collaboration avec statut 'terminee'
- Un client ne peut laisser qu'un seul avis par collaboration
- Le donneur_id vient du JWT (pas du body) pour éviter l'usurpation
- Pagination : page + limite pour l'infinite scroll mobile
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Avis, Collaboration
from app.repositories.avis_repository import AvisRepository
from app.repositories.collaboration_repository import CollaborationRepository
from typing import List, Optional, Dict, Any


class AvisService:
    """Service de gestion des avis"""

    def __init__(self, db: Session):
        self.db = db
        self.avis_repo = AvisRepository(db)
        self.collaboration_repo = CollaborationRepository(db)

    def creer_avis(
        self,
        donneur_id: str,
        receveur_id: str,
        note: int,
        commentaire: Optional[str] = None,
        collaboration_id: Optional[str] = None,
    ) -> Avis:
        """
        Créer un avis sur un freelance.

        Règles appliquées :
        1. Si collaboration_id fourni : vérifier que la collaboration est terminée
        2. Vérifier qu'un avis n'existe pas déjà pour cette collaboration
        3. Vérifier que le donneur est bien le client de la collaboration
        """
        if collaboration_id:
            collaboration = self.collaboration_repo.obtenir_par_id(collaboration_id)
            if not collaboration:
                raise ValueError("Collaboration introuvable")
            if collaboration.statut != "terminee":
                raise ValueError(
                    "Vous ne pouvez laisser un avis que sur une collaboration terminée"
                )
            if collaboration.client_id != donneur_id:
                raise PermissionError(
                    "Vous ne pouvez laisser un avis que sur vos propres collaborations"
                )
            # Anti-doublon : un seul avis par collaboration
            avis_existant = (
                self.db.query(Avis)
                .filter(
                    Avis.collaboration_id == collaboration_id,
                    Avis.donneur_id == donneur_id,
                )
                .first()
            )
            if avis_existant:
                raise ValueError("Vous avez déjà laissé un avis pour cette collaboration")

        avis = Avis(
            id=str(uuid.uuid4()),
            donneur_id=donneur_id,
            receveur_id=receveur_id,
            note=note,
            commentaire=commentaire,
            collaboration_id=collaboration_id,
        )
        return self.avis_repo.creer(avis)

    def obtenir_avis_freelance(
        self,
        freelance_id: str,
        page: int = 1,
        limite: int = 10,
    ) -> Dict[str, Any]:
        """
        Obtenir les avis d'un freelance avec pagination.

        ACTEUR : Tous (public)
        ÉCRAN   : EcranProfil (onglet Avis) — infinite scroll

        Retourne :
        {
            "avis": [...],
            "total": int,
            "page": int,
            "limite": int,
            "note_moyenne": float,
        }
        """
        avis_liste = self.avis_repo.obtenir_par_id_freelance_pagine(
            freelance_id=freelance_id,
            page=page,
            limite=limite,
        )
        total = self.avis_repo.compter_par_freelance(freelance_id)
        note_moyenne = self.avis_repo.note_moyenne_freelance(freelance_id)

        return {
            "avis": avis_liste,
            "total": total,
            "page": page,
            "limite": limite,
            "note_moyenne": round(note_moyenne, 2) if note_moyenne else 0.0,
        }
