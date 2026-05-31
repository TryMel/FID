"""
Router Vérification
====================
Vérification d'identité et de documents des utilisateurs.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranParametres (section vérification) → GET  /verification/statut
  - EcranParametres (demande vérif)        → POST /verification/demander
  - EcranDashboardAdmin (admin)            → POST /verification/repondre

ACTEURS :
  FREELANCE          → Demande la vérification de son identité/documents
  CLIENT PARTICULIER → Peut demander une vérification basique
  CLIENT ENTREPRISE  → Peut demander une vérification SIRET/entreprise
  ADMIN              → Valide ou refuse les demandes de vérification

TYPES DE VÉRIFICATION :
  - identite   : pièce d'identité (tous acteurs)
  - diplome    : diplôme ou certification (freelance)
  - entreprise : SIRET / extrait Kbis (client entreprise)
  - email      : vérification email (tous acteurs)
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from app.services.verification_service import VerificationService
from app.database import obtenir_db
from app.schemas.verification import VerificationRequest, VerificationResponse
from app.security.auth import obtenir_utilisateur_actuel
from app.security.dependencies import exiger_admin
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/statut",
    summary="Statut de vérification de l'utilisateur connecté",
    description=(
        "Retourne le statut de vérification (en_attente, validé, refusé). "
        "**Écran** : EcranParametres (badge de vérification)."
    ),
)
async def obtenir_statut_verification(
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    GET /verification/statut
    ─────────────────────────
    Tous acteurs authentifiés — Retourne le statut de vérification.
    """
    verification_service = VerificationService(db)
    return verification_service.obtenir_statut_verification(utilisateur_actuel["id"])


@router.post(
    "/demander",
    summary="Demander une vérification",
    description=(
        "Soumet une demande de vérification d'identité ou de document. "
        "**Écran** : EcranParametres (bouton 'Vérifier mon compte')."
    ),
)
async def demander_verification(
    donnees: VerificationRequest,
    request: Request,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    POST /verification/demander
    ────────────────────────────
    Tous acteurs authentifiés — Soumet une demande de vérification.
    Types : identite | diplome | entreprise | email.
    """
    verification_service = VerificationService(db)
    country = getattr(request.state, "country", "CI")
    return verification_service.demander_verification(
        utilisateur_actuel["id"], donnees.type, country
    )


@router.post(
    "/repondre",
    summary="Répondre à une demande de vérification (Admin)",
    description=(
        "Valide ou refuse une demande de vérification. "
        "**Écran** : EcranDashboardAdmin (liste des vérifications en attente)."
    ),
)
async def repondre_verification(
    verification_id: str,
    donnees: VerificationResponse,
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """
    POST /verification/repondre
    ────────────────────────────
    ADMIN uniquement — Valide ou refuse une demande.
    Statuts possibles : validé | refusé.
    """
    verification_service = VerificationService(db)
    return verification_service.repondre_verification(
        verification_id, donnees.reponse, donnees.statut
    )


@router.get(
    "/{code}",
    summary="Obtenir une vérification par code",
    description="Retourne les détails d'une vérification par son code unique.",
)
async def obtenir_verification_par_code(
    code: str,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    GET /verification/{code}
    ─────────────────────────
    Tous acteurs authentifiés — Retourne les détails d'une vérification.
    """
    verification_service = VerificationService(db)
    return verification_service.obtenir_verification_par_code(code)
