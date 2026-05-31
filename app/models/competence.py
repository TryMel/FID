import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Competence(Base):
    """Modèle de compétence"""
    __tablename__ = "competences"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"))
    nom = Column(String, nullable=False)
    niveau = Column(String)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="competences")
