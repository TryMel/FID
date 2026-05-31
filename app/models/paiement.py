import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Paiement(Base):
    """Modèle de paiement"""
    __tablename__ = "paiements"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"))
    montant = Column(Float, nullable=False)
    statut = Column(String, default="en_attente")
    type = Column(String)
    reference = Column(String)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="paiements")
