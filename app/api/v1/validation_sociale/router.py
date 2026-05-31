"""
Router Validation Sociale
==========================
Validation des liens vers les réseaux sociaux des freelances.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranEditionProfil (liens sociaux) → POST /validation-sociale/valider
  - EcranEditionProfil (domaines OK)   → GET  /validation-sociale/domaines-autorises

ACTEURS :
  FREELANCE → Valide ses liens sociaux (LinkedIn, GitHub, Dribbble, etc.)
  ADMIN     → Consulte les validations

RÈGLES PALIER :
  GRATUIT  → 1 lien social validé
  PRO      → 5 liens sociaux validés
  PREMIUM  → 5 liens sociaux validés

PLATEFORMES SUPPORTÉES :
  linkedin, github, dribbble, behance, pinterest, framer, twitter, instagram
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from app.services.validation_sociale_service import ValidationSocialeService
from app.database import obtenir_db
from app.schemas.validation_sociale import SocialValidationRequest
from app.security.dependencies import exiger_freelance
from app.repositories.auth_repository import AuthRepository
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/valider",
    summary="Valider un lien social",
    description=(
        "Valide et enregistre un lien vers un réseau social. "
        "**Écran** : EcranEditionProfil (champs liens sociaux)."
    ),
)
async def valider_lien_social(
    donnees: SocialValidationRequest,
    request: Request,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    POST /validation-sociale/valider
    ──────────────────────────────────
    FREELANCE uniquement — Valide un lien social.
    Règle palier : GRATUIT=1 lien, PRO/PREMIUM=5 liens.
    """
    validation_service = ValidationSocialeService(db)
    country = getattr(request.state, "country", "CI")
    return validation_service.valider_lien_social(
        utilisateur_actuel["id"],
        donnees.plateforme,
        donnees.url,
        country,
    )


@router.get(
    "/domaines-autorises",
    summary="Domaines de réseaux sociaux autorisés",
    description=(
        "Retourne la liste des domaines autorisés pour les liens sociaux. "
        "**Écran** : EcranEditionProfil (validation côté client)."
    ),
)
async def obtenir_domaines_autorises(
    request: Request,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    GET /validation-sociale/domaines-autorises
    ────────────────────────────────────────────
    FREELANCE uniquement — Retourne les domaines autorisés.
    Ex : linkedin.com, github.com, dribbble.com, behance.net...
    """
    validation_service = ValidationSocialeService(db)
    country = getattr(request.state, "country", "CI")
    return {"domaines": validation_service.obtenir_domaines_autorises(country)}
