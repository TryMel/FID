"""
Router Avis
============
Gestion des avis clients sur les freelances.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranProfil (onglet Avis)  → GET  /utilisateurs/{freelanceId}/avis
  - EcranProfil (laisser avis) → POST /utilisateurs/{freelanceId}/avis

ACTEURS :
  CLIENT PARTICULIER / ENTREPRISE → Laisser un avis après collaboration terminée
  FREELANCE / PUBLIC              → Consulter les avis en lecture seule
  ADMIN                           → Accès complet

RÈGLES MÉTIER :
  - Un avis ne peut être laissé que sur une collaboration avec statut 'terminee'
  - Un client ne peut laisser qu'un seul avis par collaboration
  - Le donneur_id vient du JWT (pas du body)
  - Pagination pour l'infinite scroll mobile
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from app.services.avis_service import AvisService
from app.database import obtenir_db
from app.schemas.avis import AvisCreer
from app.security.auth import obtenir_utilisateur_actuel
from app.security.dependencies import exiger_client
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/{freelanceId}/avis",
    summary="Avis d'un freelance (paginés)",
    description=(
        "Retourne les avis d'un freelance du plus récent au plus ancien. "
        "Supporte l'infinite scroll via page + limite. "
        "**Écran** : EcranProfil (onglet Avis)."
    ),
)
async def obtenir_avis_freelance(
    freelanceId: str,
    page: int = Query(1, ge=1, description="Numéro de page"),
    limite: int = Query(10, ge=1, le=50, description="Avis par page"),
    db: Session = Depends(obtenir_db),
):
    """
    GET /utilisateurs/{freelanceId}/avis?page=1&limite=10
    ───────────────────────────────────────────────────────
    Tous acteurs (public) — Retourne :
      - avis : liste paginée (avatar client, nom, note, date, commentaire)
      - total : nombre total d'avis
      - note_moyenne : note moyenne du freelance
    """
    avis_service = AvisService(db)
    return avis_service.obtenir_avis_freelance(
        freelance_id=freelanceId,
        page=page,
        limite=limite,
    )


@router.post(
    "/{freelanceId}/avis",
    summary="Laisser un avis sur un freelance",
    description=(
        "Crée un avis après une collaboration terminée. "
        "**Écran** : EcranProfil (bouton 'Laisser un avis' visible après collaboration terminée)."
    ),
)
async def creer_avis(
    freelanceId: str,
    donnees: AvisCreer,
    utilisateur_actuel: dict = Depends(exiger_client),
    db: Session = Depends(obtenir_db),
):
    """
    POST /utilisateurs/{freelanceId}/avis
    ───────────────────────────────────────
    CLIENT PARTICULIER / ENTREPRISE uniquement.
    Règles :
      - collaboration_id obligatoire pour valider que la collab est terminée
      - Un seul avis par collaboration
      - donneur_id = utilisateur connecté (JWT)
    """
    avis_service = AvisService(db)
    try:
        avis = avis_service.creer_avis(
            donneur_id=utilisateur_actuel["id"],
            receveur_id=freelanceId,
            note=donnees.note,
            commentaire=donnees.commentaire,
            collaboration_id=donnees.collaboration_id,
        )
        return avis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
