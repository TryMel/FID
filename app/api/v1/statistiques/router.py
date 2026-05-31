"""
Router Statistiques
====================
Statistiques d'activité des freelances.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranStatistiques → GET /utilisateurs/{userId}/statistiques

ACTEURS :
  FREELANCE          → Consulte ses propres statistiques (Pro/Premium uniquement)
  ADMIN              → Consulte les stats de n'importe quel utilisateur
  CLIENT             → ACCÈS REFUSÉ (les stats sont privées)

RÈGLES PALIER :
  GRATUIT  → Accès refusé (CTA Upgrade affiché côté mobile)
  PRO      → Accès complet (données des 12 derniers mois)
  PREMIUM  → Accès complet + rafraîchissement temps réel (toutes les 5 min)
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.statistiques_service import StatistiquesService
from app.database import obtenir_db
from app.security.auth import obtenir_utilisateur_actuel
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/{userId}/statistiques",
    summary="Statistiques d'un freelance",
    description=(
        "Retourne les statistiques complètes d'un freelance : projets/mois, revenus/mois, "
        "taux de réponse, taux de complétion, note moyenne. "
        "**Écran** : EcranStatistiques (onglet Statistics du profil). "
        "Accès : propriétaire Pro/Premium ou Admin uniquement."
    ),
)
async def obtenir_statistiques_utilisateur(
    userId: str,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    GET /utilisateurs/{userId}/statistiques
    ─────────────────────────────────────────
    FREELANCE (Pro/Premium) ou ADMIN uniquement.

    Retourne :
      - projets_par_mois  : dict {"YYYY-MM": int} sur 12 mois
      - revenus_par_mois  : dict {"YYYY-MM": float} sur 12 mois
      - taux_reponse      : float (%)
      - taux_completion   : float (%)
      - total_projets     : int
      - total_gains       : float
      - note_moyenne      : float

    Règles d'accès :
      - Admin : accès à tous les utilisateurs
      - Freelance : accès uniquement à ses propres stats
      - Freelance GRATUIT : 403 (CTA Upgrade côté mobile)
      - Client : 403
    """
    # Vérification des droits d'accès
    est_admin = utilisateur_actuel["role"] == "admin"
    est_proprietaire = utilisateur_actuel["id"] == userId

    if not est_admin and not est_proprietaire:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez consulter que vos propres statistiques"
        )

    # Vérification palier (sauf admin)
    if not est_admin:
        from app.repositories.auth_repository import AuthRepository
        auth_repo = AuthRepository(db)
        utilisateur = auth_repo.obtenir_par_id(userId)
        if utilisateur and utilisateur.palier == "gratuit":
            raise HTTPException(
                status_code=403,
                detail="Les statistiques sont disponibles à partir du palier Pro. Passez en Pro pour y accéder."
            )

    statistiques_service = StatistiquesService(db)
    country = "CI"  # Valeur par défaut, enrichie par le middleware de localisation
    return statistiques_service.obtenir_statistiques_utilisateur(userId, country)
