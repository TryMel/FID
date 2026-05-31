"""
Schémas Pydantic pour le Portfolio
=====================================
Validation des données pour les projets du portfolio freelance.

ACTEURS CONCERNÉS :
- FREELANCE : crée, modifie, supprime ses projets
- CLIENT / PUBLIC : lecture seule

RÈGLES PALIER :
- GRATUIT  → max 4 projets, 1 image par projet
- PRO      → max 20 projets, 5 images par projet
- PREMIUM  → max 20 projets, 5 images par projet
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class ProjetCreer(BaseModel):
    """
    Schéma de création d'un projet portfolio.
    Utilisé par : FREELANCE uniquement.
    """
    titre: str = Field(
        ..., min_length=2, max_length=150,
        description="Titre du projet (2-150 caractères)"
    )
    description: Optional[str] = Field(
        None, max_length=2000,
        description="Description du projet (max 2000 caractères)"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL de l'image principale (miniature)"
    )
    images_urls: Optional[List[str]] = Field(
        None, max_length=5,
        description="Liste d'URLs d'images supplémentaires (max 5)"
    )
    url_projet: Optional[str] = Field(
        None,
        description="URL du projet en ligne"
    )
    technologies: Optional[str] = Field(
        None, max_length=500,
        description="Technologies utilisées (texte libre)"
    )
    ordre_affichage: Optional[int] = Field(
        0, ge=0,
        description="Ordre d'affichage dans le portfolio (drag & drop)"
    )

    @field_validator("image_url", "url_projet", mode="before")
    @classmethod
    def valider_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        return v

    @field_validator("images_urls", mode="before")
    @classmethod
    def valider_images_urls(cls, v):
        if v and len(v) > 5:
            raise ValueError("Maximum 5 images par projet")
        return v


class ProjetMettreAJour(BaseModel):
    """
    Schéma de mise à jour d'un projet portfolio.
    Utilisé par : FREELANCE uniquement (propriétaire du projet).
    """
    titre: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    image_url: Optional[str] = None
    images_urls: Optional[List[str]] = Field(None, max_length=5)
    url_projet: Optional[str] = None
    technologies: Optional[str] = Field(None, max_length=500)
    ordre_affichage: Optional[int] = Field(None, ge=0)

    @field_validator("image_url", "url_projet", mode="before")
    @classmethod
    def valider_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("L'URL doit commencer par http:// ou https://")
        return v


class ProjetReponse(BaseModel):
    """Schéma de réponse pour un projet portfolio"""
    id: str
    utilisateur_id: str
    titre: str
    description: Optional[str]
    image_url: Optional[str]
    images_urls: Optional[str]   # JSON stringifié côté DB
    url_projet: Optional[str]
    technologies: Optional[str]
    ordre_affichage: int

    class Config:
        from_attributes = True


# Rétrocompatibilité (anciens noms)
ProjectCreate = ProjetCreer
ProjectUpdate = ProjetMettreAJour
