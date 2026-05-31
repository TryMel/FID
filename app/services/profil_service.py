"""
Service Profil
==============
Gère la logique métier liée aux profils utilisateurs.

ACTEURS CONCERNÉS :
- FREELANCE : gère son propre profil, expériences, compétences
- CLIENT / PUBLIC : consulte les profils en lecture seule
- ADMIN : peut modifier n'importe quel profil

RÈGLES MÉTIER :
- Pareto 80/20 : les freelances Premium (boost_visibilite=True) apparaissent en tête de recherche
- Un utilisateur ne peut modifier que son propre profil (sauf admin)
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Profil, Utilisateur, Experience, Diplome, Certification, Competence
from app.repositories.profil_repository import ProfilRepository
from typing import Optional, List, Dict, Any


class ProfilService:
    def __init__(self, db: Session):
        self.db = db
        self.profil_repo = ProfilRepository(db)

    def obtenir_profil_public(self, utilisateur_id: str):
        """
        Obtenir le profil public d'un utilisateur.
        Crée un profil vide si inexistant (première visite).
        Enrichit la réponse avec les données de l'utilisateur.
        """
        utilisateur = self.db.query(Utilisateur).filter(
            Utilisateur.id == utilisateur_id
        ).first()
        if not utilisateur:
            return None

        profil = self.profil_repo.obtenir_par_id_utilisateur(utilisateur_id)
        if not profil:
            profil = Profil(utilisateur_id=utilisateur_id)
            profil = self.profil_repo.creer(profil)

        return self._enrichir_profil(profil, utilisateur)

    def obtenir_mon_profil(self, utilisateur_id: str):
        """
        Obtenir mon profil complet.
        Crée un profil vide si inexistant (première connexion).
        """
        utilisateur = self.db.query(Utilisateur).filter(
            Utilisateur.id == utilisateur_id
        ).first()
        if not utilisateur:
            return None

        profil = self.profil_repo.obtenir_par_id_utilisateur(utilisateur_id)
        if not profil:
            profil = Profil(utilisateur_id=utilisateur_id)
            profil = self.profil_repo.creer(profil)

        return self._enrichir_profil(profil, utilisateur)

    def _enrichir_profil(self, profil: Profil, utilisateur: Utilisateur) -> dict:
        """Construit un dict de profil enrichi avec les données utilisateur."""
        return {
            "id": profil.id,
            "utilisateur_id": utilisateur.id,
            "nom": utilisateur.nom,
            "prenom": utilisateur.prenom,
            "email": utilisateur.email,
            "role": utilisateur.role,
            "type_compte": utilisateur.type_compte,
            "palier": utilisateur.palier,
            "solde_candidatures": utilisateur.solde_candidatures,
            "avatar_url": utilisateur.avatar_url,
            "nom_entreprise": utilisateur.nom_entreprise,
            "secteur_activite": utilisateur.secteur_activite,
            "site_web": utilisateur.site_web,
            # Données du profil
            "titre_professionnel": profil.titre_professionnel,
            "biographie": profil.biographie,
            "taux_horaire": profil.taux_horaire,
            "disponibilite": profil.disponibilite,
            "linkedin": profil.linkedin,
            "github": profil.github,
            "dribbble": profil.dribbble,
            "portfolio": profil.portfolio,
            "nombre_vues": profil.nombre_vues,
            "score_popularite": profil.score_popularite,
            "boost_visibilite": profil.boost_visibilite,
        }

    def mettre_a_jour_profil(self, utilisateur_id: str, titre_professionnel: Optional[str] = None,
                             biographie: Optional[str] = None, taux_horaire: Optional[float] = None,
                             disponibilite: Optional[bool] = None, current_user_id: Optional[str] = None,
                             current_user_role: Optional[str] = None):
        """
        Mettre à jour le profil.

        Règle métier : Un utilisateur ne peut modifier que son propre profil,
        sauf s'il est admin.
        """
        if current_user_id and current_user_role != "admin":
            if current_user_id != utilisateur_id:
                raise PermissionError("Tu ne peux pas modifier le profil d'un autre utilisateur")

        profil = self.obtenir_mon_profil(utilisateur_id)
        if not profil:
            profil = Profil(utilisateur_id=utilisateur_id)
            profil = self.profil_repo.creer(profil)

        if titre_professionnel:
            profil.titre_professionnel = titre_professionnel
        if biographie:
            profil.biographie = biographie
        if taux_horaire:
            profil.taux_horaire = taux_horaire
        if disponibilite is not None:
            profil.disponibilite = disponibilite

        return self.profil_repo.mettre_a_jour(profil)

    def ajouter_experience(self, utilisateur_id: str, titre: str, date_debut: str,
                           entreprise: Optional[str] = None, description: Optional[str] = None,
                           date_fin: Optional[str] = None, current_user_id: Optional[str] = None,
                           current_user_role: Optional[str] = None):
        """
        Ajouter une expérience.

        Règle métier : Un utilisateur ne peut ajouter des expériences qu'à son propre profil,
        sauf s'il est admin.
        """
        if current_user_id and current_user_role != "admin":
            if current_user_id != utilisateur_id:
                raise PermissionError("Tu ne peux pas ajouter des expériences au profil d'un autre utilisateur")

        experience = Experience(
            utilisateur_id=utilisateur_id,
            titre=titre,
            entreprise=entreprise,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin
        )
        return self.profil_repo.creer_experience(experience)

    def obtenir_experiences(self, utilisateur_id: str) -> List[Experience]:
        """Obtenir les expériences d'un utilisateur"""
        return self.profil_repo.obtenir_experiences(utilisateur_id)

    def ajouter_competence(self, utilisateur_id: str, nom: str, niveau: Optional[str] = None,
                           current_user_id: Optional[str] = None, current_user_role: Optional[str] = None):
        """
        Ajouter une compétence.

        Règle métier : Un utilisateur ne peut ajouter des compétences qu'à son propre profil,
        sauf s'il est admin.
        """
        if current_user_id and current_user_role != "admin":
            if current_user_id != utilisateur_id:
                raise PermissionError("Tu ne peux pas ajouter des compétences au profil d'un autre utilisateur")

        competence = Competence(
            utilisateur_id=utilisateur_id,
            nom=nom,
            niveau=niveau
        )
        return self.profil_repo.creer_competence(competence)

    def obtenir_competences(self, utilisateur_id: str) -> List[Competence]:
        """Obtenir les compétences d'un utilisateur"""
        return self.profil_repo.obtenir_competences(utilisateur_id)

    def rechercher_freelances(
        self,
        mot_cle: Optional[str] = None,
        disponible: Optional[bool] = None,
        palier: Optional[str] = None,
        page: int = 1,
        limite: int = 20,
    ) -> Dict[str, Any]:
        """
        Rechercher des freelances avec filtres et pagination.

        ACTEUR : CLIENT PARTICULIER, CLIENT ENTREPRISE, PUBLIC
        ÉCRAN   : EcranRechercheFreelances (GET /api/v1/utilisateurs/recherche)

        RÈGLES MÉTIER :
        - Pareto 80/20 : les freelances avec boost_visibilite=True (Premium) apparaissent
          en tête de liste pour maximiser leur visibilité.
        - Filtre par mot-clé sur titre_professionnel et biographie du profil.
        - Filtre par disponibilité (disponible=True/False).
        - Filtre par palier d'abonnement (gratuit / pro / premium).
        - Pagination standard (page, limite).
        """
        # Jointure Utilisateur ↔ Profil
        requete = (
            self.db.query(Utilisateur, Profil)
            .join(Profil, Profil.utilisateur_id == Utilisateur.id, isouter=True)
            .filter(Utilisateur.role == "freelance")
            .filter(Utilisateur.statut == "actif")
        )

        # Filtre mot-clé sur titre_professionnel ou biographie
        if mot_cle:
            terme = f"%{mot_cle}%"
            requete = requete.filter(
                or_(
                    Profil.titre_professionnel.ilike(terme),
                    Profil.biographie.ilike(terme),
                    Utilisateur.nom.ilike(terme),
                    Utilisateur.prenom.ilike(terme),
                )
            )

        # Filtre disponibilité
        if disponible is not None:
            requete = requete.filter(Profil.disponibilite == disponible)

        # Filtre palier d'abonnement
        if palier:
            requete = requete.filter(Utilisateur.palier == palier)

        # Compte total avant pagination
        total = requete.count()

        # Tri Pareto 80/20 : boost_visibilite=True en premier, puis par score_popularite desc
        requete = requete.order_by(
            Profil.boost_visibilite.desc(),
            Profil.score_popularite.desc(),
        )

        # Pagination
        decalage = (page - 1) * limite
        resultats = requete.offset(decalage).limit(limite).all()

        # Formatage de la réponse
        freelances = []
        for utilisateur, profil in resultats:
            freelances.append({
                "id": utilisateur.id,
                "nom": utilisateur.nom,
                "prenom": utilisateur.prenom,
                "palier": utilisateur.palier,
                "avatar_url": utilisateur.avatar_url,
                "titre_professionnel": profil.titre_professionnel if profil else None,
                "biographie": profil.biographie if profil else None,
                "taux_horaire": profil.taux_horaire if profil else None,
                "disponibilite": profil.disponibilite if profil else None,
                "score_popularite": profil.score_popularite if profil else 0.0,
                "boost_visibilite": profil.boost_visibilite if profil else False,
                "linkedin": profil.linkedin if profil else None,
                "github": profil.github if profil else None,
            })

        return {
            "freelances": freelances,
            "total": total,
            "page": page,
            "limite": limite,
            "pages_total": (total + limite - 1) // limite,
        }
