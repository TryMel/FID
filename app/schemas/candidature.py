"""
Schémas Pydantic pour les Candidatures
========================================
Validation des données pour les postulations de freelances aux missions.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CandidatureCreer(BaseModel):
    """
    Schéma de création d'une candidature.
    Utilisé par : FREELANCE uniquement
    """
    message_motivation: Optional[str] = Field(
        None, max_length=2000,
        description="Message de motivation du freelance (max 2000 caractères)"
    )
    tarif_propose: Optional[float] = Field(
        None, ge=0,
        description="Tarif proposé par le freelance en XOF (>= 0)"
    )
    duree_estimee: Optional[int] = Field(
        None, ge=1, le=365,
        description="Durée estimée en jours (1 à 365)"
    )


class CandidatureBooster(BaseModel):
    """
    Schéma pour booster une candidature (remonter en tête de liste).
    Fonctionnalité payante - Mimétisme social.
    Utilisé par : FREELANCE (PRO ou PREMIUM uniquement)
    """
    prioritaire: bool = Field(True, description="Activer le boost de la candidature")


class CandidatureStatutUpdate(BaseModel):
    """
    Schéma de mise à jour du statut d'une candidature.
    Utilisé par : CLIENT PARTICULIER ou CLIENT ENTREPRISE
    """
    statut: str = Field(
        ...,
        pattern="^(vue|acceptee|refusee)$",
        description="Nouveau statut : vue, acceptee ou refusee"
    )


class CandidatureReponse(BaseModel):
    """Schéma de réponse pour une candidature"""
    id: str
    collaboration_id: str
    freelance_id: str
    message_motivation: Optional[str]
    tarif_propose: Optional[float]
    duree_estimee: Optional[int]
    statut: str
    prioritaire: bool
    date_creation: Optional[datetime]
    date_modification: Optional[datetime]

    class Config:
        from_attributes = True
