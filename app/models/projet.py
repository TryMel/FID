"""
Modèle Projet (Portfolio)
==========================
Représente un projet du portfolio d'un freelance.

ACTEURS CONCERNÉS :
- FREELANCE : crée, modifie, supprime ses projets
- CLIENT / PUBLIC : consulte les projets en lecture seule

RÈGLES MÉTIER (palier) :
- GRATUIT  → max 4 projets
- PRO      → max 20 projets
- PREMIUM  → max 20 projets (illimité en pratique)
"""
import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Projet(Base):
    """Modèle de projet portfolio"""
    __tablename__ = "projets"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), nullable=False, index=True)

    # Contenu du projet
    titre = Column(String, nullable=False)
    description = Column(Text)
    image_url = Column(String)           # Image principale (miniature)
    images_urls = Column(Text)           # JSON stringifié : ["url1","url2",...] max 5 images
    url_projet = Column(String)          # Lien vers le projet en ligne
    technologies = Column(Text)          # Technologies utilisées (texte libre ou JSON)

    # Ordre d'affichage (drag & drop dans le portfolio)
    ordre_affichage = Column(Integer, default=0, nullable=False)

    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="projets")
