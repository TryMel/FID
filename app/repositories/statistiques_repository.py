"""
Repository Statistiques
========================
Fournit de vraies requêtes SQLAlchemy pour les statistiques utilisateur.

ACTEURS CONCERNÉS :
- FREELANCE : consulte ses propres statistiques (revenus, projets, taux)
- ADMIN : peut consulter les stats de n'importe quel utilisateur

RÈGLES MÉTIER :
- Les données couvrent les 12 derniers mois glissants
- taux_reponse = collaborations avec freelance assigné / total collaborations du freelance
- taux_completion = collaborations terminées / collaborations acceptées
- total_gains = somme des paiements avec statut "complete"
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Utilisateur, Collaboration, Avis, Paiement
from typing import Dict, Any, List
from datetime import datetime, timedelta
import calendar


class StatistiquesRepository:
    """Repository pour les statistiques - gère l'accès aux données statistiques"""

    def __init__(self, db: Session):
        self.db = db

    def _generer_12_derniers_mois(self) -> List[str]:
        """Génère la liste des 12 derniers mois au format 'YYYY-MM'"""
        maintenant = datetime.utcnow()
        mois = []
        for i in range(11, -1, -1):
            # Reculer de i mois
            annee = maintenant.year
            mois_num = maintenant.month - i
            while mois_num <= 0:
                mois_num += 12
                annee -= 1
            mois.append(f"{annee}-{mois_num:02d}")
        return mois

    def obtenir_projets_par_mois(self, user_id: str) -> Dict[str, int]:
        """
        Nombre de collaborations terminées par mois sur les 12 derniers mois.
        Représente les 'projets réalisés' du freelance.
        """
        maintenant = datetime.utcnow()
        debut = maintenant - timedelta(days=365)

        resultats = (
            self.db.query(
                extract("year", Collaboration.date_creation).label("annee"),
                extract("month", Collaboration.date_creation).label("mois"),
                func.count(Collaboration.id).label("total"),
            )
            .filter(
                Collaboration.freelance_id == user_id,
                Collaboration.statut == "terminee",
                Collaboration.date_creation >= debut,
            )
            .group_by("annee", "mois")
            .all()
        )

        # Construire un dict indexé par "YYYY-MM"
        donnees = {f"{int(r.annee)}-{int(r.mois):02d}": r.total for r in resultats}

        # Remplir les mois manquants avec 0
        return {mois: donnees.get(mois, 0) for mois in self._generer_12_derniers_mois()}

    def obtenir_revenus_par_mois(self, user_id: str) -> Dict[str, float]:
        """
        Revenus mensuels sur les 12 derniers mois (paiements avec statut 'complete').
        """
        maintenant = datetime.utcnow()
        debut = maintenant - timedelta(days=365)

        resultats = (
            self.db.query(
                extract("year", Paiement.date_creation).label("annee"),
                extract("month", Paiement.date_creation).label("mois"),
                func.sum(Paiement.montant).label("total"),
            )
            .filter(
                Paiement.utilisateur_id == user_id,
                Paiement.statut == "complete",
                Paiement.date_creation >= debut,
            )
            .group_by("annee", "mois")
            .all()
        )

        donnees = {f"{int(r.annee)}-{int(r.mois):02d}": float(r.total) for r in resultats}
        return {mois: donnees.get(mois, 0.0) for mois in self._generer_12_derniers_mois()}

    def obtenir_statistiques_utilisateur(self, user_id: str, country: str) -> Dict[str, Any]:
        """
        Retourne les statistiques complètes d'un utilisateur.

        Structure retournée :
        {
            "projets_par_mois": {"YYYY-MM": int, ...},
            "revenus_par_mois": {"YYYY-MM": float, ...},
            "taux_reponse": float,
            "taux_completion": float,
            "total_projets": int,
            "total_gains": float,
            "note_moyenne": float,
        }
        """
        utilisateur = self.db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
        if not utilisateur:
            return {}

        # ── Projets par mois ──────────────────────────────────────────
        projets_par_mois = self.obtenir_projets_par_mois(user_id)

        # ── Revenus par mois ──────────────────────────────────────────
        revenus_par_mois = self.obtenir_revenus_par_mois(user_id)

        # ── Total projets (collaborations terminées) ──────────────────
        total_projets = (
            self.db.query(func.count(Collaboration.id))
            .filter(
                Collaboration.freelance_id == user_id,
                Collaboration.statut == "terminee",
            )
            .scalar() or 0
        )

        # ── Total gains ───────────────────────────────────────────────
        total_gains = (
            self.db.query(func.sum(Paiement.montant))
            .filter(
                Paiement.utilisateur_id == user_id,
                Paiement.statut == "complete",
            )
            .scalar() or 0.0
        )

        # ── Taux de réponse : collaborations avec freelance assigné / total ──
        total_collab = (
            self.db.query(func.count(Collaboration.id))
            .filter(Collaboration.freelance_id == user_id)
            .scalar() or 0
        )
        collab_avec_reponse = (
            self.db.query(func.count(Collaboration.id))
            .filter(
                Collaboration.freelance_id == user_id,
                Collaboration.statut.in_(["en_cours", "terminee"]),
            )
            .scalar() or 0
        )
        taux_reponse = round(collab_avec_reponse / total_collab * 100, 1) if total_collab > 0 else 0.0

        # ── Taux de complétion : terminées / (en_cours + terminées) ──
        collab_acceptees = (
            self.db.query(func.count(Collaboration.id))
            .filter(
                Collaboration.freelance_id == user_id,
                Collaboration.statut.in_(["en_cours", "terminee"]),
            )
            .scalar() or 0
        )
        taux_completion = round(total_projets / collab_acceptees * 100, 1) if collab_acceptees > 0 else 0.0

        # ── Note moyenne ──────────────────────────────────────────────
        note_moyenne = (
            self.db.query(func.avg(Avis.note))
            .filter(Avis.receveur_id == user_id)
            .scalar() or 0.0
        )

        return {
            "projets_par_mois": projets_par_mois,
            "revenus_par_mois": revenus_par_mois,
            "taux_reponse": taux_reponse,
            "taux_completion": taux_completion,
            "total_projets": total_projets,
            "total_gains": float(total_gains),
            "note_moyenne": round(float(note_moyenne), 2),
        }
