import uuid
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Collaboration(Base):
    """Modèle de collaboration"""
    __tablename__ = "collaborations"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("utilisateurs.id"))
    freelance_id = Column(String, ForeignKey("utilisateurs.id"), nullable=True)
    titre = Column(String, nullable=False)
    description = Column(Text)
    statut = Column(String, default="en_attente")
    budget = Column(Float)
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    
    # Nouveaux champs demandés
    photos = Column(Text, nullable=True)  # URLs séparées par des virgules
    zone_intervention = Column(String, nullable=True)
    type_client = Column(String, default="particulier")  # "particulier" ou "entreprise"
    limite_temps = Column(DateTime(timezone=True), nullable=True)
    prioritaire = Column(Boolean, default=False)  # Pour la monétisation (mission premium/prioritaire)
    
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("Utilisateur", foreign_keys=[client_id], back_populates="collaborations_client")
    freelance = relationship("Utilisateur", foreign_keys=[freelance_id], back_populates="collaborations_freelance")
    candidatures = relationship("Candidature", back_populates="collaboration", cascade="all, delete-orphan")
