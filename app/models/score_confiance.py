import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ScoreConfiance(Base):
    """Modèle de score de confiance"""
    __tablename__ = "scores_confiance"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), unique=True)
    score = Column(Float, default=0)
    nombre_avis = Column(Integer, default=0)
    nombre_projets = Column(Integer, default=0)
    verification_complete = Column(Boolean, default=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="score_confiance")
