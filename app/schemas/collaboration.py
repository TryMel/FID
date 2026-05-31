"""
Schémas Pydantic pour les Collaborations (missions)
======================================================
Validation des données pour les missions publiées par les clients.

ACTEURS CONCERNÉS :
- CLIENT PARTICULIER : peut publier des missions à durée déterminée
  → limite_temps obligatoire, budget modéré
- CLIENT ENTREPRISE : peut publier des missions sans limite de temps particulière
  → accès aux freelances Elite/Club20 en priorité
- FREELANCE : voit la liste des missions et peut consulter les détails
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CollaborationCreer(BaseModel):
    """
    Schéma de création d'une mission.
    Utilisé par : CLIENT PARTICULIER ou CLIENT ENTREPRISE
    """
    titre: str = Field(
        ..., min_length=2, max_length=200,
        description="Titre de la mission (2-200 caractères)"
    )
    description: Optional[str] = Field(
        None, max_length=5000,
        description="Description détaillée de la mission (max 5000 caractères)"
    )
    budget: Optional[float] = Field(None, ge=0, description="Budget alloué en XOF (>= 0)")
    date_debut: Optional[str] = Field(None, description="Date de début souhaitée YYYY-MM-DD")
    date_fin: Optional[str] = Field(None, description="Date de fin souhaitée YYYY-MM-DD")

    # Nouveaux champs
    photos: Optional[str] = Field(
        None,
        description="URLs des photos séparées par des virgules (ex: url1,url2)"
    )
    zone_intervention: Optional[str] = Field(
        None, max_length=200,
        description="Zone géographique d'intervention (ville, pays...)"
    )
    limite_temps: Optional[str] = Field(
        None,
        description="Date limite pour postuler à la mission YYYY-MM-DD"
    )
    prioritaire: bool = Field(
        False,
        description="Mission prioritaire/urgente (visible en premier pour les freelances PREMIUM)"
    )


class CollaborationMettreAJour(BaseModel):
    """
    Schéma de mise à jour du statut d'une mission.
    Utilisé par : CLIENT PARTICULIER, CLIENT ENTREPRISE ou FREELANCE (partiel)
    """
    statut: str = Field(
        ...,
        pattern="^(en_attente|acceptée|en_cours|terminée|annulée)$",
        description="Statut : en_attente, acceptée, en_cours, terminée ou annulée"
    )


class CollaborationReponse(BaseModel):
    """Schéma de réponse complet pour une mission"""
    id: str
    client_id: str
    freelance_id: Optional[str]
    titre: str
    description: Optional[str]
    statut: str
    budget: Optional[float]
    date_debut: Optional[datetime]
    date_fin: Optional[datetime]
    photos: Optional[str]
    zone_intervention: Optional[str]
    type_client: Optional[str]
    limite_temps: Optional[datetime]
    prioritaire: bool
    nombre_candidatures: Optional[int] = Field(
        None,
        description="Nombre de freelances ayant postulé (preuve sociale - Mimétisme)"
    )
    date_creation: Optional[datetime]

    class Config:
        from_attributes = True
