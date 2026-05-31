"""
Modèle Candidature
==================
Représente la postulation d'un freelance à une mission (collaboration).

ACTEURS CONCERNÉS :
- FREELANCE : soumet une candidature à une mission (décrémente son solde si gratuit - Jevons)
- CLIENT PARTICULIER : voit les candidatures reçues sur sa mission et accepte/refuse
- CLIENT ENTREPRISE : idem mais peut avoir plus de missions actives

RÈGLES MÉTIER :
- Un freelance ne peut postuler qu'une fois par mission
- Les freelances GRATUITS ont un quota de 3 candidatures/mois (Paradoxe de Jevons)
- Les freelances PRO ont 15 candidatures/mois
- Les freelances PREMIUM ont un quota illimité
- Une candidature "prioritaire" (boostée) remonte en tête de liste chez le client
- Le client voit le nombre de candidatures = preuve sociale (Mimétisme de Girard)
"""
import uuid
from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Candidature(Base):
    """Modèle de candidature d'un freelance à une mission"""
    __tablename__ = "candidatures"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    collaboration_id = Column(String, ForeignKey("collaborations.id"), nullable=False, index=True)
    freelance_id = Column(String, ForeignKey("utilisateurs.id"), nullable=False, index=True)

    # Contenu de la candidature
    message_motivation = Column(Text, nullable=True)
    tarif_propose = Column(Float, nullable=True)        # Tarif proposé par le freelance (en XOF ou devise locale)
    duree_estimee = Column(Integer, nullable=True)       # Durée estimée en jours

    # Statut de la candidature
    statut = Column(String, default="en_attente")       # "en_attente", "vue", "acceptee", "refusee"

    # Fonctionnalité de boost payant (Mimétisme social - candidature mise en avant)
    prioritaire = Column(Boolean, default=False)         # True = candidature boostée/vedette (option payante)

    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    collaboration = relationship("Collaboration", back_populates="candidatures")
    freelance = relationship("Utilisateur", back_populates="candidatures")

    # Contrainte : un freelance ne peut postuler qu'une fois par mission
    __table_args__ = (
        UniqueConstraint("collaboration_id", "freelance_id", name="uq_candidature_collab_freelance"),
    )
