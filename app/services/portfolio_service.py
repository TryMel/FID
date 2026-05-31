"""
Service Portfolio
==================
Logique métier pour la gestion des projets portfolio des freelances.

ACTEURS CONCERNÉS :
- FREELANCE : crée, modifie, supprime, réordonne ses projets
- CLIENT / PUBLIC : consulte les projets en lecture seule

RÈGLES PALIER (Paradoxe de Jevons) :
- GRATUIT  → max 4 projets  (frustration calculée → incite à upgrader)
- PRO      → max 20 projets
- PREMIUM  → max 20 projets
"""
import json
from sqlalchemy.orm import Session
from app.models import Projet, Utilisateur
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.auth_repository import AuthRepository
from typing import List, Optional

# Quotas de projets par palier
QUOTAS_PROJETS = {"gratuit": 4, "pro": 20, "premium": 20}


class PortfolioService:
    """Service de gestion du portfolio"""

    def __init__(self, db: Session):
        self.db = db
        self.portfolio_repo = PortfolioRepository(db)
        self.auth_repo = AuthRepository(db)

    def obtenir_projets_utilisateur(self, utilisateur_id: str) -> List[Projet]:
        """
        Obtenir les projets d'un utilisateur triés par ordre_affichage.
        ACTEUR : Tous (public)
        ÉCRAN   : EcranProfil (grille portfolio) + EcranPortfolio (liste complète)
        """
        return (
            self.db.query(Projet)
            .filter(Projet.utilisateur_id == utilisateur_id)
            .order_by(Projet.ordre_affichage.asc(), Projet.date_creation.desc())
            .all()
        )

    def creer_projet(
        self,
        utilisateur_id: str,
        titre: str,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        images_urls: Optional[List[str]] = None,
        url_projet: Optional[str] = None,
        technologies: Optional[str] = None,
        ordre_affichage: int = 0,
    ) -> Projet:
        """
        Créer un nouveau projet portfolio.
        ACTEUR : FREELANCE uniquement.
        Vérifie le quota selon le palier avant création.
        """
        utilisateur = self.auth_repo.obtenir_par_id(utilisateur_id)
        if not utilisateur:
            raise ValueError("Utilisateur introuvable")

        # Vérification quota palier
        if not self.verifier_quota_projet(utilisateur_id, utilisateur.palier):
            quota = QUOTAS_PROJETS.get(utilisateur.palier, 4)
            raise ValueError(
                f"Limite de {quota} projets atteinte pour le palier {utilisateur.palier}. "
                "Passez au Pro pour en ajouter jusqu'à 20."
            )

        # Sérialiser images_urls en JSON
        images_json = json.dumps(images_urls) if images_urls else None

        projet = Projet(
            utilisateur_id=utilisateur_id,
            titre=titre,
            description=description,
            image_url=image_url,
            images_urls=images_json,
            url_projet=url_projet,
            technologies=technologies,
            ordre_affichage=ordre_affichage,
        )
        return self.portfolio_repo.creer(projet)

    def obtenir_projet(self, projet_id: str) -> Optional[Projet]:
        """Obtenir un projet par son ID"""
        return self.portfolio_repo.obtenir_par_id(projet_id)

    def mettre_a_jour_projet(
        self,
        projet_id: str,
        proprietaire_id: str,
        titre: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        images_urls: Optional[List[str]] = None,
        url_projet: Optional[str] = None,
        technologies: Optional[str] = None,
        ordre_affichage: Optional[int] = None,
    ) -> Optional[Projet]:
        """
        Mettre à jour un projet.
        ACTEUR : FREELANCE propriétaire uniquement.
        """
        projet = self.obtenir_projet(projet_id)
        if not projet:
            raise ValueError("Projet introuvable")
        if projet.utilisateur_id != proprietaire_id:
            raise PermissionError("Vous ne pouvez modifier que vos propres projets")

        if titre is not None:
            projet.titre = titre
        if description is not None:
            projet.description = description
        if image_url is not None:
            projet.image_url = image_url
        if images_urls is not None:
            projet.images_urls = json.dumps(images_urls)
        if url_projet is not None:
            projet.url_projet = url_projet
        if technologies is not None:
            projet.technologies = technologies
        if ordre_affichage is not None:
            projet.ordre_affichage = ordre_affichage

        return self.portfolio_repo.mettre_a_jour(projet)

    def supprimer_projet(self, projet_id: str, proprietaire_id: str) -> bool:
        """
        Supprimer un projet.
        ACTEUR : FREELANCE propriétaire uniquement.
        """
        projet = self.obtenir_projet(projet_id)
        if not projet:
            raise ValueError("Projet introuvable")
        if projet.utilisateur_id != proprietaire_id:
            raise PermissionError("Vous ne pouvez supprimer que vos propres projets")
        return self.portfolio_repo.supprimer(projet_id)

    def verifier_quota_projet(self, utilisateur_id: str, palier: str) -> bool:
        """Vérifier si l'utilisateur peut ajouter un projet selon son palier"""
        nb_projets = self.portfolio_repo.compter_par_id_utilisateur(utilisateur_id)
        quota = QUOTAS_PROJETS.get(palier, 4)
        return nb_projets < quota
