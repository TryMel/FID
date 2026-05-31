from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CodeQR(Base):
    """Modèle de code QR"""
    __tablename__ = "codes_qr"

    id = Column(String, primary_key=True, index=True)
    utilisateur_id = Column(String, ForeignKey("utilisateurs.id"), unique=True)
    code = Column(String, unique=True)
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="code_qr")
