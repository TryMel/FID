"""
Schémas Pydantic pour les Abonnements
========================================
Validation des données pour la gestion des souscriptions freelance.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AbonnementCheckout(BaseModel):
    """Schéma pour initier un checkout de paiement"""
    palier: str = Field(
        ...,
        pattern="^(pro|premium)$",
        description="Palier cible : pro ou premium (pas gratuit)"
    )


class AbonnementMettreAJour(BaseModel):
    """Schéma pour activer un abonnement après paiement confirmé"""
    palier: str = Field(
        ...,
        pattern="^(gratuit|pro|premium)$",
        description="Nouveau palier actif"
    )
    reference_paiement: Optional[str] = Field(
        None,
        description="Référence du paiement (ID session Stripe/Moneroo)"
    )


class ConfirmationEmailAbonnement(BaseModel):
    """Schéma pour l'envoi de l'email de confirmation"""
    palier: str = Field(
        ...,
        pattern="^(pro|premium)$",
        description="Palier souscrit"
    )
    date_effet: str = Field(
        ...,
        description="Date d'effet de l'abonnement (ISO 8601)"
    )


class AbonnementReponse(BaseModel):
    """Schéma de réponse pour l'abonnement actif"""
    palier: str
    date_debut: Optional[datetime]
    date_expiration: Optional[datetime]
    est_actif: bool
    solde_candidatures: Optional[int]
    renouvellement_automatique: bool = True

    class Config:
        from_attributes = True
