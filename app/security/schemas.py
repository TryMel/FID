from pydantic import BaseModel, Field
from typing import Optional


class TokenResponse(BaseModel):
    """Schéma pour la réponse de token"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """Schéma pour le payload du token JWT"""
    sub: str  # user_id
    email: str
    role: str
    exp: int


class LoginRequest(BaseModel):
    """Schéma pour la requête de connexion"""
    email: str = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., min_length=1, description="Mot de passe")


class RegisterRequest(BaseModel):
    """Schéma pour la requête d'inscription"""
    email: str = Field(..., description="Email de l'utilisateur")
    password: str = Field(..., min_length=8, description="Mot de passe (min 8 caractères)")
    nom_complet: str = Field(..., min_length=2, description="Nom complet")
    role: str = Field(default="freelance", description="Rôle (freelance, client, admin)")


class PasswordChangeRequest(BaseModel):
    """Schéma pour le changement de mot de passe"""
    current_password: str = Field(..., description="Mot de passe actuel")
    new_password: str = Field(..., min_length=8, description="Nouveau mot de passe (min 8 caractères)")


class PasswordResetRequest(BaseModel):
    """Schéma pour la réinitialisation de mot de passe"""
    email: str = Field(..., description="Email de l'utilisateur")


class PasswordResetConfirm(BaseModel):
    """Schéma pour la confirmation de réinitialisation de mot de passe"""
    token: str = Field(..., description="Token de réinitialisation")
    new_password: str = Field(..., min_length=8, description="Nouveau mot de passe (min 8 caractères)")
