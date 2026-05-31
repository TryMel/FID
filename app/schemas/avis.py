"""
Schémas Pydantic pour les Avis
================================
Validation des données pour les avis clients sur les freelances.

ACTEURS CONCERNÉS :
- CLIENT PARTICULIER / ENTREPRISE : laisse un avis après une collaboration terminée
- FREELANCE / PUBLIC : consulte les avis en lecture seule

RÈGLES MÉTIER :
- Un avis ne peut être laissé que sur une collaboration avec statut 'terminee'
- Un client ne peut laisser qu'un seul avis par collaboration
- Le donneur_id vient du JWT (pas du body) pour éviter l'usurpation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AvisCreer(BaseModel):
    """
    Schéma de création d'un avis.
    Utilisé par : CLIENT PARTICULIER ou CLIENT ENTREPRISE.
    Note : donneur_id est injecté depuis le JWT côté serveur.
    """
    note: int = Field(
        ..., ge=1, le=5,
        description="Note de 1 à 5 étoiles"
    )
    commentaire: Optional[str] = Field(
        None, max_length=1000,
        description="Commentaire textuel (max 1000 caractères)"
    )
    collaboration_id: Optional[str] = Field(
        None,
        description="ID de la collaboration associée (obligatoire pour valider l'avis)"
    )


class AvisReponse(BaseModel):
    """Schéma de réponse pour un avis"""
    id: str
    donneur_id: str
    receveur_id: str
    note: int
    commentaire: Optional[str]
    collaboration_id: Optional[str]
    date_creation: Optional[datetime]

    class Config:
        from_attributes = True


# Rétrocompatibilité
AvisCreate = AvisCreer
