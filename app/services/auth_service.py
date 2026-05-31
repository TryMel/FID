from sqlalchemy.orm import Session
from app.models import Utilisateur
from app.repositories.auth_repository import AuthRepository
import bcrypt
from typing import Optional

# Quotas initiaux de candidatures selon le palier (Paradoxe de Jevons)
QUOTAS_INITIAUX = {"gratuit": 3, "pro": 15, "premium": 9999}


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_repo = AuthRepository(db)

    def inscrire_utilisateur(
        self,
        email: str,
        password: str,
        nom_complet: str,
        role: str = "freelance",
        type_compte: Optional[str] = None,
        nom_entreprise: Optional[str] = None,
        siret: Optional[str] = None,
        secteur_activite: Optional[str] = None,
        site_web: Optional[str] = None,
    ):
        """Inscription d'un nouvel utilisateur"""
        # Vérifier si l'email existe déjà via le repository
        existing_user = self.auth_repo.obtenir_par_email(email)
        if existing_user:
            raise ValueError("Email déjà utilisé")

        # Déduire le type_compte si non fourni
        if type_compte is None:
            type_compte = role  # "freelance" → "freelance", "client" → "particulier" par défaut

        # Hash du mot de passe
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Création de l'utilisateur avec tous les champs
        user = Utilisateur(
            email=email,
            mot_de_passe=hashed_password.decode("utf-8"),
            nom=nom_complet,
            role=role,
            type_compte=type_compte,
            palier="gratuit",
            solde_candidatures=QUOTAS_INITIAUX["gratuit"],
            nom_entreprise=nom_entreprise,
            siret=siret,
            secteur_activite=secteur_activite,
            site_web=site_web,
        )

        # Utiliser le repository pour créer l'utilisateur
        return self.auth_repo.creer(user)

    def authentifier_utilisateur(self, email: str, password: str):
        """Authentification d'un utilisateur"""
        user = self.auth_repo.obtenir_par_email(email)
        
        if not user:
            raise ValueError("Identifiants invalides")
        
        # Vérification du mot de passe
        if not bcrypt.checkpw(password.encode('utf-8'), user.mot_de_passe.encode('utf-8')):
            raise ValueError("Identifiants invalides")
        
        return user

    def obtenir_utilisateur_par_id(self, user_id: str):
        """Obtenir un utilisateur par son ID"""
        return self.auth_repo.obtenir_par_id(user_id)
