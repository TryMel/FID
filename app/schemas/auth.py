"""
Schémas Pydantic pour l'Authentification
==========================================
Gestion de l'inscription et connexion des 4 types d'acteurs :
- FREELANCE : crée un profil professionnel avec compétences, portfolio, etc.
- CLIENT PARTICULIER : publie des petites missions ponctuelles
- CLIENT ENTREPRISE : publie des projets, accède aux freelances Elite
- ADMIN : gestion de la plateforme
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class InscriptionRequest(BaseModel):
    """
    Schéma d'inscription pour tous les acteurs.
    Le champ 'role' détermine le type de compte.
    """
    email: EmailStr
    password: str = Field(
        ..., min_length=8, max_length=100,
        description="Mot de passe (min 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre)"
    )
    nom_complet: str = Field(
        ..., min_length=2, max_length=100,
        description="Nom complet (2-100 caractères)"
    )
    role: str = Field(
        default="freelance",
        pattern="^(freelance|client|admin)$",
        description="Rôle : freelance, client ou admin"
    )
    type_compte: str = Field(
        default="freelance",
        pattern="^(freelance|particulier|entreprise)$",
        description="Type de compte : freelance, particulier ou entreprise"
    )

    # Champs optionnels pour les entreprises
    nom_entreprise: Optional[str] = Field(None, max_length=200, description="Nom de l'entreprise (client entreprise)")
    siret: Optional[str] = Field(None, max_length=20, description="Numéro SIRET (client entreprise)")
    secteur_activite: Optional[str] = Field(None, max_length=100, description="Secteur d'activité")
    site_web: Optional[str] = Field(None, max_length=500, description="Site web de l'entreprise")

    @field_validator('password')
    @classmethod
    def valider_mot_de_passe(cls, v):
        """Valider la complexité du mot de passe"""
        if not any(c.isupper() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not any(c.islower() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not any(c.isdigit() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v


class ConnexionRequest(BaseModel):
    """Schéma de connexion - valable pour tous les acteurs"""
    email: EmailStr
    password: str


class UtilisateurReponse(BaseModel):
    """Schéma de réponse utilisateur (sans mot de passe)"""
    id: str
    email: str
    nom: str
    role: str
    type_compte: str
    palier: str
    solde_candidatures: int
    nom_entreprise: Optional[str] = None
    secteur_activite: Optional[str] = None
    site_web: Optional[str] = None

    class Config:
        from_attributes = True


class AuthReponse(BaseModel):
    """Réponse d'authentification avec token JWT"""
    user: UtilisateurReponse
    token: str
    token_type: str = "bearer"


# Rétrocompatibilité (anciens noms)
RegisterRequest = InscriptionRequest
LoginRequest = ConnexionRequest
UserResponse = UtilisateurReponse
AuthResponse = AuthReponse
