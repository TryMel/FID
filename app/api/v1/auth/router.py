from fastapi import APIRouter, HTTPException, Depends
from app.services.auth_service import AuthService
from app.database import obtenir_db
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse, AuthResponse
from app.security.jwt import creer_token_acces
from sqlalchemy.orm import Session
from datetime import timedelta
from app.config import settings

router = APIRouter()


def _construire_reponse_user(user) -> UserResponse:
    """Construit un UserResponse complet depuis un objet Utilisateur SQLAlchemy."""
    return UserResponse(
        id=user.id,
        email=user.email,
        nom=user.nom,
        role=user.role,
        type_compte=user.type_compte or user.role,
        palier=user.palier or "gratuit",
        solde_candidatures=user.solde_candidatures if user.solde_candidatures is not None else 3,
        nom_entreprise=user.nom_entreprise,
        secteur_activite=user.secteur_activite,
        site_web=user.site_web,
    )


@router.post("/register", response_model=AuthResponse)
async def inscrire(request: RegisterRequest, db: Session = Depends(obtenir_db)):
    """
    Inscription d'un nouvel utilisateur.

    ACTEURS : FREELANCE | CLIENT PARTICULIER | CLIENT ENTREPRISE
    ÉCRAN MOBILE : EcranInscription
    """
    auth_service = AuthService(db)
    try:
        user = auth_service.inscrire_utilisateur(
            email=request.email,
            password=request.password,
            nom_complet=request.nom_complet,
            role=request.role,
            type_compte=request.type_compte,
            nom_entreprise=getattr(request, "nom_entreprise", None),
            siret=getattr(request, "siret", None),
            secteur_activite=getattr(request, "secteur_activite", None),
            site_web=getattr(request, "site_web", None),
        )
        token = creer_token_acces(
            data={"sub": user.id, "email": user.email, "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return AuthResponse(user=_construire_reponse_user(user), token=token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def connexion(request: LoginRequest, db: Session = Depends(obtenir_db)):
    """
    Connexion d'un utilisateur existant.

    ACTEURS : FREELANCE | CLIENT PARTICULIER | CLIENT ENTREPRISE
    ÉCRAN MOBILE : EcranConnexion
    """
    auth_service = AuthService(db)
    try:
        user = auth_service.authentifier_utilisateur(
            email=request.email,
            password=request.password,
        )
        token = creer_token_acces(
            data={"sub": user.id, "email": user.email, "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return AuthResponse(user=_construire_reponse_user(user), token=token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
