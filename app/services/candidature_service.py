"""
Service Candidature
====================
Logique métier complète pour les postulations de freelances.

RÈGLES MÉTIER PAR ACTEUR :
────────────────────────────────────────────────────────────────────────────────
FREELANCE GRATUIT  → Quota 3 candidatures/mois (Paradoxe de Jevons)
                     Doit cibler ses candidatures avec soin
FREELANCE PRO      → Quota 15 candidatures/mois
                     Peut booster 1 candidature/mois
FREELANCE PREMIUM  → Quota illimité
                     Peut voir les missions prioritaires 24h avant les autres
                     Peut booster toutes ses candidatures

CLIENT PARTICULIER → Reçoit les candidatures et peut accepter/refuser
                     Ses missions sont limitées (pas de prolongation infinie)
CLIENT ENTREPRISE  → Reçoit les candidatures et peut accepter/refuser
                     Accès aux candidatures des freelances Elite (Club 20)
────────────────────────────────────────────────────────────────────────────────

EFFETS ÉCONOMIQUES INTÉGRÉS :
- Jevons : quota de candidatures → force la qualité sur la quantité
- Mimétisme (Girard) : indicateur de "X freelances ont postulé" visible par le client
- Pareto 80/20 : les freelances Elite (Club 20, score >= 80) remontent automatiquement
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional, List

from app.models.candidature import Candidature
from app.models.utilisateur import Utilisateur
from app.models.collaboration import Collaboration
from app.repositories.candidature_repository import CandidatureRepository
from app.repositories.auth_repository import AuthRepository
from app.repositories.collaboration_repository import CollaborationRepository


# ─────────────────────────────────────────────────────────────────────
# Quotas de candidatures selon le palier (Paradoxe de Jevons)
# ─────────────────────────────────────────────────────────────────────
QUOTAS_CANDIDATURES = {
    "gratuit": 3,    # 3 candidatures/mois → force la réflexion
    "pro": 15,       # 15 candidatures/mois
    "premium": 9999  # Illimité
}


class CandidatureService:
    """Service de gestion des candidatures (postulations)"""

    def __init__(self, db: Session):
        self.db = db
        self.candidature_repo = CandidatureRepository(db)
        self.auth_repo = AuthRepository(db)
        self.collaboration_repo = CollaborationRepository(db)

    def postuler(
        self,
        collaboration_id: str,
        freelance_id: str,
        message_motivation: Optional[str] = None,
        tarif_propose: Optional[float] = None,
        duree_estimee: Optional[int] = None,
    ) -> Candidature:
        """
        Soumettre une candidature à une mission.

        Règles appliquées :
        1. Vérifie que la mission existe et est ouverte
        2. Vérifie que le postulant est bien un freelance
        3. Vérifie que le freelance n'a pas déjà postulé (unicité)
        4. Vérifie et décrémente le solde de candidatures (Paradoxe de Jevons)
        5. Pour les freelances GRATUIT : refuse si la mission est PRIORITAIRE et <24h
        """
        # 1. Vérifier que la mission existe
        collaboration = self.collaboration_repo.obtenir_par_id(collaboration_id)
        if not collaboration:
            raise ValueError("Mission introuvable")
        if collaboration.statut not in ["en_attente", "en_cours"]:
            raise ValueError("Cette mission n'accepte plus de candidatures")

        # 2. Vérifier que c'est bien un freelance
        freelance = self.auth_repo.obtenir_par_id(freelance_id)
        if not freelance:
            raise ValueError("Compte freelance introuvable")
        if freelance.role != "freelance":
            raise ValueError("Seuls les freelances peuvent postuler à une mission")

        # 3. Anti-doublon
        if self.candidature_repo.candidature_existante(collaboration_id, freelance_id):
            raise ValueError("Tu as déjà postulé à cette mission")

        # 4. Vérification et décrémentation du quota Jevons (sauf Premium)
        if freelance.palier != "premium":
            if freelance.solde_candidatures <= 0:
                raise ValueError(
                    f"Quota de candidatures épuisé pour ce mois-ci. "
                    f"Passez en Premium pour des candidatures illimitées."
                )
            # Décrémenter le solde
            freelance.solde_candidatures -= 1
            self.db.commit()

        # 5. Restriction accès missions prioritaires (Jevons + Monétisation)
        if collaboration.prioritaire and freelance.palier == "gratuit":
            # Vérifier si la mission a été publiée depuis moins de 24h
            if collaboration.date_creation:
                age_mission = datetime.utcnow() - collaboration.date_creation.replace(tzinfo=None)
                if age_mission < timedelta(hours=24):
                    raise ValueError(
                        "Les missions prioritaires sont réservées aux freelances Pro et Premium "
                        "pendant les premières 24 heures. Passez en Pro pour un accès anticipé."
                    )

        # Créer la candidature
        candidature = Candidature(
            id=str(uuid.uuid4()),
            collaboration_id=collaboration_id,
            freelance_id=freelance_id,
            message_motivation=message_motivation,
            tarif_propose=tarif_propose,
            duree_estimee=duree_estimee,
            statut="en_attente",
            prioritaire=False,
        )
        return self.candidature_repo.creer(candidature)

    def booster_candidature(self, candidature_id: str, freelance_id: str) -> Candidature:
        """
        Booster une candidature pour qu'elle apparaisse en premier chez le client.
        Fonctionnalité payante (PRO ou PREMIUM uniquement).
        Mimétisme social : déclenche l'envie du client de regarder en premier.
        """
        candidature = self.candidature_repo.obtenir_par_id(candidature_id)
        if not candidature:
            raise ValueError("Candidature introuvable")
        if candidature.freelance_id != freelance_id:
            raise PermissionError("Tu ne peux booster que tes propres candidatures")

        freelance = self.auth_repo.obtenir_par_id(freelance_id)
        if freelance.palier == "gratuit":
            raise ValueError(
                "Le boost de candidature est disponible à partir du palier Pro. "
                "Passez en Pro pour mettre votre candidature en avant."
            )

        return self.candidature_repo.activer_boost(candidature_id)

    def changer_statut_candidature(
        self,
        candidature_id: str,
        nouveau_statut: str,
        client_id: str,
    ) -> Candidature:
        """
        Accepter ou refuser une candidature.
        Utilisé par : CLIENT PARTICULIER ou CLIENT ENTREPRISE

        Si acceptée : met à jour le freelance_id de la collaboration
        """
        candidature = self.candidature_repo.obtenir_par_id(candidature_id)
        if not candidature:
            raise ValueError("Candidature introuvable")

        # Vérifier que le client est bien le propriétaire de la mission
        collaboration = self.collaboration_repo.obtenir_par_id(candidature.collaboration_id)
        if not collaboration:
            raise ValueError("Mission introuvable")
        if collaboration.client_id != client_id:
            raise PermissionError("Tu ne peux gérer que les candidatures de tes missions")

        # Si on accepte, on lie le freelance à la collaboration
        if nouveau_statut == "acceptee":
            collaboration.freelance_id = candidature.freelance_id
            collaboration.statut = "en_cours"
            self.db.commit()

        return self.candidature_repo.mettre_a_jour_statut(candidature_id, nouveau_statut)

    def obtenir_candidatures_mission(
        self, collaboration_id: str, client_id: str
    ) -> dict:
        """
        Retourner toutes les candidatures d'une mission pour le client.
        Inclut le nombre total (preuve sociale / Mimétisme de Girard).
        Triées : boostées (payantes) en premier, puis par date.
        """
        collaboration = self.collaboration_repo.obtenir_par_id(collaboration_id)
        if not collaboration:
            raise ValueError("Mission introuvable")
        if collaboration.client_id != client_id:
            raise PermissionError("Tu ne peux voir que les candidatures de tes missions")

        candidatures = self.candidature_repo.obtenir_par_collaboration(collaboration_id)
        return {
            "total": len(candidatures),
            "candidatures": candidatures,
        }

    def obtenir_mes_candidatures(self, freelance_id: str) -> List[Candidature]:
        """Retourner toutes les candidatures soumises par un freelance"""
        return self.candidature_repo.obtenir_par_freelance(freelance_id)

    def reinitialiser_solde_mensuel(self, utilisateur_id: str) -> None:
        """
        Réinitialiser le solde de candidatures au début d'un nouveau mois.
        À appeler via un script cron ou au moment de la connexion mensuelle.
        Les abonnés Premium ne sont pas concernés.
        """
        utilisateur = self.auth_repo.obtenir_par_id(utilisateur_id)
        if not utilisateur:
            return
        quota = QUOTAS_CANDIDATURES.get(utilisateur.palier, 3)
        utilisateur.solde_candidatures = quota
        self.db.commit()
