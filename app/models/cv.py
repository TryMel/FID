from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CV(Base):
    """Modèle de CV"""
    __tablename__ = "cv"

    id = Column(String, primary_key=True, index=True)
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), unique=True)
    template_id = Column(String)
    contenu = Column(Text)
    url_pdf = Column(String)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="cv")
