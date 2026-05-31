from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Certification(Base):
    """Modèle de certification"""
    __tablename__ = "certifications"

    id = Column(String, primary_key=True, index=True)
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"))
    titre = Column(String, nullable=False)
    organisme = Column(String)
    date_obtention = Column(DateTime(timezone=True))
    url_certificat = Column(String)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="certifications")
