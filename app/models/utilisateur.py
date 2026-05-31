import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Utilisateur(Base):
    """Modèle d'utilisateur"""
    __tablename__ = "utilisateurs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    mot_de_passe = Column(String, nullable=False)
    nom = Column(String, nullable=False)
    prenom = Column(String)
    role = Column(String, default="freelance")
    telephone = Column(String)
    avatar_url = Column(String)
    statut = Column(String, default="actif")
    email_verifie = Column(Boolean, default=False)
    
    # Nouveaux champs pour la monétisation, l'abonnement et les types de compte
    type_compte = Column(String, default="freelance")  # "freelance", "entreprise", "particulier"
    palier = Column(String, default="gratuit")  # "gratuit", "pro", "premium"
    date_fin_abonnement = Column(DateTime(timezone=True), nullable=True)
    solde_candidatures = Column(Integer, default=3)  # Pour Jevons Paradox (Quota gratuit initial)
    
    # Détails entreprise / client particulier
    nom_entreprise = Column(String, nullable=True)
    description_entreprise = Column(Text, nullable=True)
    secteur_activite = Column(String, nullable=True)
    siret = Column(String, nullable=True)
    adresse = Column(String, nullable=True)
    site_web = Column(String, nullable=True)
    
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    profil = relationship("Profil", back_populates="utilisateur", uselist=False)
    experiences = relationship("Experience", back_populates="utilisateur")
    diplomes = relationship("Diplome", back_populates="utilisateur")
    certifications = relationship("Certification", back_populates="utilisateur")
    competences = relationship("Competence", back_populates="utilisateur")
    projets = relationship("Projet", back_populates="utilisateur")
    collaborations_client = relationship("Collaboration", foreign_keys="Collaboration.client_id", back_populates="client")
    collaborations_freelance = relationship("Collaboration", foreign_keys="Collaboration.freelance_id", back_populates="freelance")
    avis_donne = relationship("Avis", foreign_keys="Avis.donneur_id", back_populates="donneur")
    avis_recu = relationship("Avis", foreign_keys="Avis.receveur_id", back_populates="receveur")
    paiements = relationship("Paiement", back_populates="utilisateur")
    score_confiance = relationship("ScoreConfiance", back_populates="utilisateur", uselist=False)
    code_qr = relationship("CodeQR", back_populates="utilisateur", uselist=False)
    verifications = relationship("Verification", back_populates="utilisateur")
    validations_sociales = relationship("ValidationSociale", back_populates="utilisateur")
    cv = relationship("CV", back_populates="utilisateur", uselist=False)
    candidatures = relationship("Candidature", back_populates="freelance")
