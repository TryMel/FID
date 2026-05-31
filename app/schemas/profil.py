from pydantic import BaseModel, Field, validator
from typing import Optional


class ProfilUpdate(BaseModel):
    titre_professionnel: Optional[str] = Field(None, max_length=200, description="Titre professionnel (max 200 caractères)")
    biographie: Optional[str] = Field(None, max_length=2000, description="Biographie (max 2000 caractères)")
    taux_horaire: Optional[float] = Field(None, ge=0, le=10000, description="Taux horaire entre 0 et 10000")
    disponibilite: Optional[bool] = None


class ExperienceCreate(BaseModel):
    titre: str = Field(..., min_length=2, max_length=200, description="Titre de l'expérience (2-200 caractères)")
    date_debut: str = Field(..., description="Date de début au format YYYY-MM-DD")
    entreprise: Optional[str] = Field(None, max_length=200, description="Entreprise (max 200 caractères)")
    description: Optional[str] = Field(None, max_length=2000, description="Description (max 2000 caractères)")
    date_fin: Optional[str] = Field(None, description="Date de fin au format YYYY-MM-DD")


class CompetenceCreate(BaseModel):
    nom: str = Field(..., min_length=2, max_length=100, description="Nom de la compétence (2-100 caractères)")
    niveau: Optional[str] = Field(None, pattern="^(débutant|intermédiaire|avancé|expert)$", description="Niveau : débutant, intermédiaire, avancé ou expert")
