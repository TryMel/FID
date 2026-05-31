from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import obtenir_db
from app.repositories.auth_repository import AuthRepository
from app.config import settings
from typing import Optional
from jose import jwt, JWTError

security = HTTPBearer()


async def obtenir_utilisateur_actuel(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(obtenir_db)
) -> dict:
    """
    Dépendance pour obtenir l'utilisateur actuel à partir du token JWT
    
    Règle globale : Vérifie que le token est valide et retourne les infos utilisateur
    
    Utilisation :
        @router.get("/mon-profil")
        async def obtenir_profil(user = Depends(obtenir_utilisateur_actuel)):
            return {"user": user}
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide : utilisateur non trouvé"
            )
        
        # Vérifier que l'utilisateur existe toujours en base
        auth_repo = AuthRepository(db)
        user = auth_repo.obtenir_par_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé"
            )
        
        if user.statut != "actif":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte désactivé"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "role": user.role,
            "statut": user.statut
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )


async def obtenir_utilisateur_optionnel(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(obtenir_db)
) -> Optional[dict]:
    """
    Dépendance pour obtenir l'utilisateur actuel de manière optionnelle
    Ne lève pas d'erreur si le token est absent ou invalide
    
    Utilisation pour les routes publiques qui peuvent bénéficier de l'authentification
    
    Utilisation :
        @router.get("/public")
        async def donnees_publiques(user = Depends(obtenir_utilisateur_optionnel)):
            if user:
                return {"data": "...", "user": user["email"]}
            return {"data": "..."}
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        auth_repo = AuthRepository(db)
        user = auth_repo.obtenir_par_id(user_id)
        if not user or user.statut != "actif":
            return None
        
        return {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "role": user.role,
            "statut": user.statut
        }
        
    except JWTError:
        return None
