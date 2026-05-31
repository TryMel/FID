"""
Router Générateur CV
=====================
Génération de CV PDF pour les freelances.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranGenerateurCV → GET  /generateur-cv/modeles
  - EcranGenerateurCV → POST /generateur-cv/generer
  - EcranGenerateurCV → GET  /generateur-cv/moi

ACTEURS :
  FREELANCE Pro     → 3 templates disponibles
  FREELANCE Premium → Templates illimités
  FREELANCE Gratuit → Accès refusé (CTA Upgrade côté mobile)
  CLIENT / ADMIN    → Accès refusé (fonctionnalité freelance uniquement)

RÈGLES PALIER :
  GRATUIT  → 403 (CTA Upgrade : "Disponible à partir du palier Pro")
  PRO      → 3 templates (moderne, classique, créatif)
  PREMIUM  → Tous les templates (illimité)
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from app.services.generateur_cv_service import GenerateurCVService
from app.database import obtenir_db
from app.schemas.generateur_cv import CVGenerateRequest
from app.security.dependencies import exiger_freelance
from app.security.auth import obtenir_utilisateur_actuel
from app.repositories.auth_repository import AuthRepository
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/modeles",
    summary="Templates de CV disponibles",
    description=(
        "Retourne la liste des templates de CV disponibles selon la langue. "
        "**Écran** : EcranGenerateurCV (sélection template)."
    ),
)
async def obtenir_modeles(
    request: Request,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    GET /generateur-cv/modeles
    ───────────────────────────
    FREELANCE Pro/Premium uniquement.
    Retourne les templates filtrés selon la langue (header Accept-Language).
    """
    # Vérifier le palier
    auth_repo = AuthRepository(db)
    utilisateur = auth_repo.obtenir_par_id(utilisateur_actuel["id"])
    if not utilisateur or utilisateur.palier == "gratuit":
        raise HTTPException(
            status_code=403,
            detail="La génération de CV est disponible à partir du palier Pro. Passez en Pro pour y accéder."
        )

    cv_service = GenerateurCVService(db)
    locale = getattr(request.state, "locale", "fr-FR")
    langue = locale.split("-")[0] if "-" in locale else locale
    return cv_service.obtenir_templates(langue)


@router.post(
    "/generer",
    summary="Générer un CV PDF",
    description=(
        "Génère un CV PDF à partir du profil du freelance et du template choisi. "
        "**Écran** : EcranGenerateurCV (bouton 'Générer mon CV')."
    ),
)
async def generer_cv(
    donnees: CVGenerateRequest,
    request: Request,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    POST /generateur-cv/generer
    ────────────────────────────
    FREELANCE Pro/Premium uniquement.
    Règles :
      - GRATUIT  → 403
      - PRO      → 3 templates max
      - PREMIUM  → illimité
    """
    auth_repo = AuthRepository(db)
    utilisateur = auth_repo.obtenir_par_id(utilisateur_actuel["id"])
    palier = utilisateur.palier if utilisateur else "gratuit"

    cv_service = GenerateurCVService(db)
    try:
        return cv_service.generer_cv(
            utilisateur_id=utilisateur_actuel["id"],
            template_id=donnees.template_id,
            langue=donnees.langue,
            palier=palier,
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get(
    "/moi",
    summary="Mon CV généré",
    description=(
        "Retourne le dernier CV généré par le freelance connecté. "
        "**Écran** : EcranGenerateurCV (aperçu + téléchargement)."
    ),
)
async def obtenir_mon_cv(
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    GET /generateur-cv/moi
    ───────────────────────
    FREELANCE uniquement — Retourne le CV existant ou null si aucun.
    """
    cv_service = GenerateurCVService(db)
    cv = cv_service.obtenir_mon_cv(utilisateur_actuel["id"])
    if not cv:
        return {"cv": None, "message": "Aucun CV généré. Utilisez POST /generer pour créer votre CV."}
    return cv


@router.get(
    "/{cvId}",
    summary="Obtenir un CV par ID",
    description="Retourne un CV spécifique par son identifiant.",
)
async def obtenir_cv(
    cvId: str,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    GET /generateur-cv/{cvId}
    ──────────────────────────
    FREELANCE propriétaire ou ADMIN uniquement.
    """
    cv_service = GenerateurCVService(db)
    cv = cv_service.obtenir_cv(cvId)
    if not cv:
        raise HTTPException(status_code=404, detail="CV non trouvé")
    # Vérifier que le CV appartient à l'utilisateur (sauf admin)
    if utilisateur_actuel["role"] != "admin" and cv.utilisateur_id != utilisateur_actuel["id"]:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return cv
