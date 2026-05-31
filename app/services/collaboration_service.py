"""
Service Collaboration (Missions)
==================================
Logique métier pour la gestion des missions publiées par les clients.

RÈGLES PAR ACTEUR :
─────────────────────────────────────────────────────────────────────
CLIENT PARTICULIER → Peut créer des missions à durée limitée
                     Max 2 missions actives simultanées
                     Accès aux freelances standard (pas Club 20 en priorité)
CLIENT ENTREPRISE  → Peut créer des missions sans limite de temps
                     Missions actives illimitées
                     Voir les profils Elite (Club 20) en premier
FREELANCE GRATUIT  → Voit les missions (sauf prioritaires <24h)
FREELANCE PRO/PREMIUM → Voit les missions prioritaires immédiatement
─────────────────────────────────────────────────────────────────────

LOGIQUE PARETO (80/20) : Les missions "prioritaires" des clients entreprises
sont présentées en premier aux freelances Elite (Club 20), maximisant la valeur
des 20% de top freelances qui génèrent 80% de la satisfaction client.
"""
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List

from app.models.collaboration import Collaboration
from app.models.utilisateur import Utilisateur
from app.repositories.collaboration_repository import CollaborationRepository
from app.repositories.auth_repository import AuthRepository
from app.repositories.candidature_repository import CandidatureRepository


# Limite de missions actives simultanées pour les clients particuliers
LIMITE_MISSIONS_PARTICULIER = 2


class CollaborationService:
    """Service de gestion des missions/collaborations"""

    def __init__(self, db: Session):
        self.db = db
        self.collaboration_repo = CollaborationRepository(db)
        self.auth_repo = AuthRepository(db)
        self.candidature_repo = CandidatureRepository(db)

    def creer_mission(
        self,
        client_id: str,
        titre: str,
        description: Optional[str] = None,
        budget: Optional[float] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        photos: Optional[str] = None,
        zone_intervention: Optional[str] = None,
        limite_temps: Optional[str] = None,
        prioritaire: bool = False,
    ) -> Collaboration:
        """
        Créer une nouvelle mission.

        Règles appliquées :
        - CLIENT PARTICULIER : limité à 2 missions actives (statut en_attente ou en_cours)
        - CLIENT ENTREPRISE : illimité
        - La mission est automatiquement marquée 'prioritaire' si le client l'active
        - Seul un client (particulier ou entreprise) peut créer une mission
        """
        client = self.auth_repo.obtenir_par_id(client_id)
        if not client:
            raise ValueError("Client introuvable")
        if client.role != "client":
            raise ValueError("Seuls les clients peuvent publier des missions")

        # Règle : les particuliers ont une limite de missions actives
        if client.type_compte == "particulier":
            missions_actives = [
                c for c in self.collaboration_repo.obtenir_par_client(client_id)
                if c.statut in ["en_attente", "en_cours"]
            ]
            if len(missions_actives) >= LIMITE_MISSIONS_PARTICULIER:
                raise ValueError(
                    f"Les clients particuliers sont limités à {LIMITE_MISSIONS_PARTICULIER} missions actives. "
                    "Terminez ou annulez une mission avant d'en créer une nouvelle."
                )

        collaboration = Collaboration(
            id=str(uuid.uuid4()),
            client_id=client_id,
            titre=titre,
            description=description,
            budget=budget,
            photos=photos,
            zone_intervention=zone_intervention,
            type_client=client.type_compte,
            prioritaire=prioritaire,
            statut="en_attente",
        )
        return self.collaboration_repo.creer(collaboration)

    def obtenir_toutes_missions(self, freelance_palier: str = "gratuit") -> List[dict]:
        """
        Retourner la liste des missions disponibles pour un freelance.

        Logique d'accès :
        - FREELANCE PREMIUM/PRO → Voit toutes les missions y compris prioritaires récentes
        - FREELANCE GRATUIT → Ne voit pas les missions prioritaires publiées <24h
        - Tri : prioritaires en tête (Pareto), puis par date de création
        """
        toutes = self.collaboration_repo.obtenir_toutes()
        maintenant = datetime.utcnow()
        result = []

        for c in toutes:
            if c.statut not in ["en_attente"]:
                continue  # N'afficher que les missions ouvertes

            # Restriction Jevons + Monétisation : missions prioritaires réservées 24h
            if c.prioritaire and freelance_palier == "gratuit" and c.date_creation:
                age = maintenant - c.date_creation.replace(tzinfo=None)
                if age < timedelta(hours=24):
                    continue  # Masquer pour les gratuits

            # Nombre de candidatures (preuve sociale = Mimétisme de Girard)
            nb_candidatures = self.candidature_repo.compter_par_collaboration(c.id)

            result.append({
                "id": c.id,
                "titre": c.titre,
                "description": c.description,
                "budget": c.budget,
                "zone_intervention": c.zone_intervention,
                "type_client": c.type_client,
                "prioritaire": c.prioritaire,
                "limite_temps": c.limite_temps,
                "photos": c.photos,
                "nombre_candidatures": nb_candidatures,  # Mimétisme social
                "date_creation": c.date_creation,
            })

        # Tri : missions prioritaires d'abord (Pareto 80/20), puis par date
        result.sort(key=lambda x: (not x["prioritaire"], x["date_creation"]))
        return result

    def obtenir_detail_mission(self, collaboration_id: str) -> Optional[dict]:
        """
        Retourner le détail complet d'une mission.
        Inclut le nombre de candidatures (preuve sociale).
        """
        collaboration = self.collaboration_repo.obtenir_par_id(collaboration_id)
        if not collaboration:
            return None
        nb_candidatures = self.candidature_repo.compter_par_collaboration(collaboration_id)
        return {
            **collaboration.__dict__,
            "nombre_candidatures": nb_candidatures,
        }

    def obtenir_missions_client(self, client_id: str) -> List[Collaboration]:
        """Retourner toutes les missions d'un client (particulier ou entreprise)"""
        return self.collaboration_repo.obtenir_par_client(client_id)

    def mettre_a_jour_statut(self, collaboration_id: str, statut: str) -> Optional[Collaboration]:
        """Mettre à jour le statut d'une mission"""
        return self.collaboration_repo.mettre_a_jour_statut(collaboration_id, statut)

    def obtenir_toutes_collaborations(self) -> List[Collaboration]:
        """Obtenir toutes les collaborations (admin)"""
        return self.collaboration_repo.obtenir_toutes()

    def obtenir_collaboration(self, collaboration_id: str) -> Optional[Collaboration]:
        """Obtenir une collaboration par son ID"""
        return self.collaboration_repo.obtenir_par_id(collaboration_id)

    def mettre_a_jour_statut_collaboration(self, collaboration_id: str, statut: str) -> Optional[Collaboration]:
        """Mettre à jour le statut d'une collaboration"""
        return self.collaboration_repo.mettre_a_jour_statut(collaboration_id, statut)

    def obtenir_collaborations_utilisateur(self, user_id: str, role: str) -> List[Collaboration]:
        """Obtenir les collaborations d'un utilisateur selon son rôle"""
        collaborations = self.collaboration_repo.obtenir_toutes()
        if role == "client":
            return [c for c in collaborations if c.client_id == user_id]
        else:
            return [c for c in collaborations if c.freelance_id == user_id]

    def creer_collaboration(
        self,
        client_id: str,
        freelance_id: str,
        titre: str,
        description: Optional[str] = None,
        budget: Optional[float] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
    ) -> Collaboration:
        """Rétrocompatibilité avec l'ancien service"""
        collaboration = Collaboration(
            id=str(uuid.uuid4()),
            client_id=client_id,
            freelance_id=freelance_id,
            titre=titre,
            description=description,
            budget=budget,
        )
        return self.collaboration_repo.creer(collaboration)
