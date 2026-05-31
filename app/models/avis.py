import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Avis(Base):
    """Modèle d'avis"""
    __tablename__ = "avis"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    donneur_id = Column(String, ForeignKey("utilisateurs.id"))
    receveur_id = Column(String, ForeignKey("utilisateurs.id"))
    collaboration_id = Column(String)
    note = Column(Integer)
    commentaire = Column(Text)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    donneur = relationship("Utilisateur", foreign_keys=[donneur_id], back_populates="avis_donne")
    receveur = relationship("Utilisateur", foreign_keys=[receveur_id], back_populates="avis_recu")
