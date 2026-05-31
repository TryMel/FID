"""
Router Score de Confiance
==========================
Score calculé reflétant la fiabilité d'un freelance.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranProfil (badge score)  → GET /score-confiance/{userId}
  - EcranParametres (mon score) → GET /score-confiance/moi

ACTEURS :
  FREELANCE Pro/Premium → Voit son propre score (valeur numérique + niveau)
  FREELANCE Gratuit     → Score masqué (CTA Upgrade côté mobile)
  CLIENT                → Voit le score des freelances (si Pro/Premium)
  ADMIN                 → Accès complet

NIVEAUX :
  0-39  → Faible   (rouge)
  40-59 → Moyen    (orange)
  60-79 → Élevé    (vert)
  80+   → Premium  (doré)

CALCUL :
  score = min(100, note_moyenne×20 + nb_avis×2 + nb_projets_terminés×3)
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.score_confiance_service import ScoreConfianceService
from app.database import obtenir_db
from app.security.auth import obtenir_utilisateur_actuel, obtenir_utilisateur_optionnel
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter()


@router.get(
    "/moi",
    summary="Mon score de confiance",
    description=(
        "Retourne le score de confiance de l'utilisateur connecté. "
        "**Écran** : EcranParametres (section score de confiance). "
        "Visible uniquement pour les freelances Pro/Premium."
    ),
)
async def obtenir_mon_score(
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    GET /score-confiance/moi
    ─────────────────────────
    FREELANCE uniquement — Retourne :
      - score : valeur numérique (0-100)
      - niveau : Faible | Moyen | Élevé | Premium
      - visible : bool (False si palier Gratuit)
    """
    score_service = ScoreConfianceService(db)
    score = score_service.obtenir_mon_score(utilisateur_actuel["id"])
    if not score:
        raise HTTPException(status_code=404, detail="Score non trouvé")
    return score


@router.post(
    "/moi/recalculer",
    summary="Recalculer mon score de confiance",
    description=(
        "Déclenche le recalcul du score de confiance. "
        "Appelé automatiquement après chaque avis reçu ou projet terminé."
    ),
)
async def recalculer_mon_score(
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    POST /score-confiance/moi/recalculer
    ──────────────────────────────────────
    FREELANCE uniquement — Recalcule et sauvegarde le score.
    """
    score_service = ScoreConfianceService(db)
    return score_service.mettre_a_jour_score(utilisateur_actuel["id"])


@router.get(
    "/{userId}",
    summary="Score de confiance d'un utilisateur (public)",
    description=(
        "Retourne le score de confiance d'un freelance. "
        "La valeur numérique n'est visible que si le freelance est Pro/Premium. "
        "**Écran** : EcranProfil (badge score à côté du nom)."
    ),
)
async def obtenir_score_utilisateur(
    userId: str,
    visiteur: Optional[dict] = Depends(obtenir_utilisateur_optionnel),
    db: Session = Depends(obtenir_db),
):
    """
    GET /score-confiance/{userId}
    ──────────────────────────────
    Tous acteurs (public) — Retourne :
      - score  : valeur numérique si freelance Pro/Premium, sinon null
      - niveau : Faible | Moyen | Élevé | Premium (si visible)
      - visible : bool

    Règle : le score n'est visible que si le PROPRIÉTAIRE du profil
    est sur le palier Pro ou Premium (pas selon le visiteur).
    """
    score_service = ScoreConfianceService(db)

    # Récupérer le palier du propriétaire du profil
    from app.repositories.auth_repository import AuthRepository
    auth_repo = AuthRepository(db)
    proprietaire = auth_repo.obtenir_par_id(userId)
    palier_proprietaire = proprietaire.palier if proprietaire else "gratuit"

    return score_service.obtenir_score_utilisateur(userId, palier_proprietaire)
