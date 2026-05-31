from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime, timedelta
from app.config import settings
from sqlalchemy.orm import Session
from app.database import obtenir_db
from app.repositories.auth_repository import AuthRepository


security = HTTPBearer()


def creer_token_acces(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Créer un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verifier_token(token: str) -> dict:
    """Vérifier un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def middleware_jwt(request: Request, call_next):
    """
    Middleware JWT pour vérifier l'authentification
    
    Règle globale : Vérifie que le token est présent et valide
    Les routes spécifiques peuvent utiliser les dépendances pour des vérifications plus fines
    """
    # Routes publiques qui ne nécessitent pas d'authentification
    public_paths = [
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/",
        "/health",
        "/docs",
        "/openapi.json"
    ]
    
    # Vérifier si la route est publique
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)
    
    # Vérifier le token pour les routes protégées
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token manquant",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = authorization.split(" ")[1]
        payload = verifier_token(token)
        
        # Stocker les informations utilisateur dans l'état de la requête
        request.state.user_id = payload.get("sub")
        request.state.user_email = payload.get("email")
        request.state.user_role = payload.get("role")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erreur d'authentification",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    response = await call_next(request)
    return response
