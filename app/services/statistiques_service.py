"""
Service Statistiques
=====================
Logique métier pour les statistiques d'activité des freelances.

ACTEURS CONCERNÉS :
- FREELANCE Pro/Premium : consulte ses propres statistiques
- ADMIN                 : consulte les stats de n'importe quel utilisateur
- CLIENT               : accès refusé

RÈGLES PALIER :
- GRATUIT  → 403 (CTA Upgrade côté mobile)
- PRO      → Accès complet (12 derniers mois)
- PREMIUM  → Accès complet + rafraîchissement toutes les 5 min

DONNÉES RETOURNÉES :
- projets_par_mois  : dict {"YYYY-MM": int} — 12 mois glissants
- revenus_par_mois  : dict {"YYYY-MM": float} — 12 mois glissants
- taux_reponse      : float (%) — collaborations répondues / total
- taux_completion   : float (%) — projets terminés / projets acceptés
- total_projets     : int — total des projets terminés
- total_gains       : float — somme des paiements confirmés
- note_moyenne      : float — moyenne des avis reçus
"""
from sqlalchemy.orm import Session
from app.repositories.statistiques_repository import StatistiquesRepository
from typing import Dict, Any


class StatistiquesService:
    """Service de gestion des statistiques"""

    def __init__(self, db: Session):
        self.db = db
        self.stats_repo = StatistiquesRepository(db)

    def obtenir_statistiques_utilisateur(
        self, utilisateur_id: str, country: str = "CI"
    ) -> Dict[str, Any]:
        """
        Retourne les statistiques complètes d'un utilisateur.

        ACTEUR : FREELANCE Pro/Premium ou ADMIN
        ÉCRAN   : EcranStatistiques

        Délègue au repository pour les vraies requêtes SQL.
        """
        return self.stats_repo.obtenir_statistiques_utilisateur(utilisateur_id, country)
