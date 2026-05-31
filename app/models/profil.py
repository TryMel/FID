import uuid
from sqlalchemy import Column, String, Text, Boolean, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Profil(Base):
    """Modèle de profil utilisateur"""
    __tablename__ = "profils"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), unique=True)
    titre_professionnel = Column(String)
    biographie = Column(Text)
    taux_horaire = Column(Float)
    disponibilite = Column(Boolean, default=True)
    linkedin = Column(String)
    github = Column(String)
    dribbble = Column(String)
    portfolio = Column(String)
    
    # Mimétisme social & visibilité premium
    nombre_vues = Column(Integer, default=0)
    score_popularite = Column(Float, default=0.0)
    boost_visibilite = Column(Boolean, default=False)
    
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="profil")
