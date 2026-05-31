"""
Router Code QR
===============
Génération et gestion du QR code professionnel des freelances.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranCodeQR → GET  /code-qr/moi
  - EcranCodeQR → POST /code-qr/generer

ACTEURS :
  FREELANCE Pro/Premium → Génère et partage son QR code
  FREELANCE Gratuit     → Accès refusé (CTA Upgrade côté mobile)
  CLIENT / PUBLIC       → Peut scanner le QR code (lien deep link)
  ADMIN                 → Accès complet

QR CODE CONTENU :
  Deep link : https://freelanceid.app/profil/{userId}
  Permet de partager rapidement son profil (Share Sheet native iOS/Android)

RÈGLES PALIER :
  GRATUIT  → 403 (CTA Upgrade : "Disponible à partir du palier Pro")
  PRO      → QR code standard
  PREMIUM  → QR code standard (même fonctionnalité)
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.code_qr_service import CodeQRService
from app.database import obtenir_db
from app.security.dependencies import exiger_freelance
from app.repositories.auth_repository import AuthRepository
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/moi",
    summary="Mon QR code professionnel",
    description=(
        "Retourne le QR code existant du freelance connecté. "
        "**Écran** : EcranCodeQR (affichage + partage via Share Sheet)."
    ),
)
async def obtenir_mon_code_qr(
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    GET /code-qr/moi
    ─────────────────
    FREELANCE Pro/Premium uniquement.
    Retourne :
      - available : bool (False si palier Gratuit)
      - exists    : bool (True si QR code déjà généré)
      - code      : deep link URL
      - url_image : URL de l'image PNG du QR code
    """
    auth_repo = AuthRepository(db)
    utilisateur = auth_repo.obtenir_par_id(utilisateur_actuel["id"])
    palier = utilisateur.palier if utilisateur else "gratuit"

    qr_service = CodeQRService(db)
    return qr_service.obtenir_mon_code_qr(utilisateur_actuel["id"], palier)


@router.post(
    "/generer",
    summary="Générer mon QR code",
    description=(
        "Génère ou régénère le QR code professionnel du freelance. "
        "**Écran** : EcranCodeQR (bouton 'Générer mon QR Code')."
    ),
)
async def generer_code_qr(
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    POST /code-qr/generer
    ──────────────────────
    FREELANCE Pro/Premium uniquement.
    Génère un QR code contenant le deep link vers le profil.
    Si un QR code existe déjà, il est mis à jour.
    """
    auth_repo = AuthRepository(db)
    utilisateur = auth_repo.obtenir_par_id(utilisateur_actuel["id"])
    palier = utilisateur.palier if utilisateur else "gratuit"

    qr_service = CodeQRService(db)
    try:
        return qr_service.generer_code_qr(utilisateur_actuel["id"], palier)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
