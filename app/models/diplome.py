import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Diplome(Base):
    """Modèle de diplôme"""
    __tablename__ = "diplomes"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"))
    titre = Column(String, nullable=False)
    etablissement = Column(String)
    annee_obtention = Column(Integer)
    description = Column(Text)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="diplomes")
