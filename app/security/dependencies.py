from fastapi import Depends, HTTPException, status
from app.security.auth import obtenir_utilisateur_actuel, obtenir_utilisateur_optionnel
from typing import Optional, List


def exiger_role(*allowed_roles: str):
    """
    Dépendance factory pour vérifier que l'utilisateur a un rôle autorisé
    
    Règle globale : Vérifie les rôles au niveau des routes
    
    Utilisation :
        @router.get("/admin")
        async def route_admin(user = Depends(exiger_role("admin"))):
            return {"message": "Admin only"}
        
        @router.get("/protected")
        async def route_protegee(user = Depends(exiger_role("admin", "freelance"))):
            return {"message": "Admin or freelance"}
    """
    def verificateur_role(current_user: dict = Depends(obtenir_utilisateur_actuel)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé : rôles autorisés : {', '.join(allowed_roles)}"
            )
        return current_user
    return verificateur_role


def exiger_admin(current_user: dict = Depends(obtenir_utilisateur_actuel)) -> dict:
    """
    Dépendance pour vérifier que l'utilisateur est admin
    
    Règle globale : Vérifie le rôle admin
    
    Utilisation :
        @router.get("/admin/dashboard")
        async def tableau_de_bord(user = Depends(exiger_admin)):
            return {"stats": "..."}
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user


def exiger_freelance(current_user: dict = Depends(obtenir_utilisateur_actuel)) -> dict:
    """
    Dépendance pour vérifier que l'utilisateur est freelance
    
    Règle globale : Vérifie le rôle freelance
    """
    if current_user["role"] != "freelance":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux freelances"
        )
    return current_user


def exiger_client(current_user: dict = Depends(obtenir_utilisateur_actuel)) -> dict:
    """
    Dépendance pour vérifier que l'utilisateur est client
    
    Règle globale : Vérifie le rôle client
    """
    if current_user["role"] != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux clients"
        )
    return current_user


def exiger_freelance_ou_client(current_user: dict = Depends(obtenir_utilisateur_actuel)) -> dict:
    """
    Dépendance pour vérifier que l'utilisateur est freelance ou client
    
    Règle globale : Vérifie les rôles freelance et client
    """
    if current_user["role"] not in ["freelance", "client"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux freelances et clients"
        )
    return current_user
