"""
Router Profil
==============
Gestion des profils utilisateurs.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranProfil (lecture publique)   → GET  /utilisateurs/{id}/profil-public
  - EcranParametres (mon profil)     → GET  /utilisateurs/moi/profil
  - EcranEditionProfil               → PATCH /utilisateurs/moi/profil
  - EcranRechercheFreelances         → GET  /utilisateurs/recherche

ACTEURS :
  FREELANCE          → Lire et modifier son propre profil
  CLIENT PARTICULIER → Lire les profils publics, rechercher des freelances
  CLIENT ENTREPRISE  → Idem + accès aux freelances Elite (score >= 80)
  ADMIN              → Accès complet
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from app.services.profil_service import ProfilService
from app.database import obtenir_db
from app.schemas.profil import ProfilUpdate, ExperienceCreate, CompetenceCreate
from app.security.auth import obtenir_utilisateur_actuel, obtenir_utilisateur_optionnel
from app.security.dependencies import exiger_freelance
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────
# ROUTES PUBLIQUES (lecture)
# ─────────────────────────────────────────────────────────────────────

@router.get(
    "/{id}/profil-public",
    summary="Profil public d'un utilisateur",
    description=(
        "Retourne le profil public d'un freelance ou client. "
        "Accessible sans authentification. "
        "**Écran mobile** : EcranProfil (lecture)."
    ),
)
async def obtenir_profil_public(
    id: str,
    visiteur: Optional[dict] = Depends(obtenir_utilisateur_optionnel),
    db: Session = Depends(obtenir_db),
):
    """
    GET /utilisateurs/{id}/profil-public
    ─────────────────────────────────────
    Tous acteurs (public) — Retourne :
      - Infos de base (nom, titre, bio, avatar, disponibilité)
      - KPIs (projets, gains, note moyenne)
      - Liens sociaux (filtrés selon palier du propriétaire)
      - Score de confiance (visible si propriétaire Pro/Premium)
      - Badge palier (Pro vert / Premium doré)
    """
    profil_service = ProfilService(db)
    profil = profil_service.obtenir_profil_public(id)
    if not profil:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return profil


@router.get(
    "/recherche",
    summary="Rechercher des freelances",
    description=(
        "Recherche paginée de freelances avec filtres. "
        "Les freelances Premium apparaissent en tête (is_featured=True). "
        "**Écran mobile** : EcranRechercheFreelances."
    ),
)
async def rechercher_freelances(
    q: Optional[str] = Query(None, description="Mot-clé (nom, titre, compétence)"),
    disponible: Optional[bool] = Query(None, description="Filtrer par disponibilité"),
    palier: Optional[str] = Query(None, description="Filtrer par palier : pro, premium"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    limite: int = Query(20, ge=1, le=100, description="Résultats par page"),
    db: Session = Depends(obtenir_db),
):
    """
    GET /utilisateurs/recherche
    ────────────────────────────
    Tous acteurs (public) — Retourne une liste paginée de freelances.
    Tri : Premium (is_featured) en tête → Pareto 80/20.
    """
    profil_service = ProfilService(db)
    return profil_service.rechercher_freelances(
        mot_cle=q,
        disponible=disponible,
        palier=palier,
        page=page,
        limite=limite,
    )


# ─────────────────────────────────────────────────────────────────────
# ROUTES AUTHENTIFIÉES — MON PROFIL
# ─────────────────────────────────────────────────────────────────────

@router.get(
    "/moi/profil",
    summary="Mon profil complet",
    description="Retourne le profil complet de l'utilisateur connecté. Crée un profil vide si première connexion. **Écran mobile** : EcranParametres.",
)
async def obtenir_mon_profil(
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    profil_service = ProfilService(db)
    profil = profil_service.obtenir_mon_profil(utilisateur_actuel["id"])
    if not profil:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return profil


@router.patch(
    "/moi/profil",
    summary="Modifier mon profil",
    description=(
        "Met à jour les informations du profil de l'utilisateur connecté. "
        "**Écran mobile** : EcranEditionProfil."
    ),
)
async def mettre_a_jour_mon_profil(
    donnees_profil: ProfilUpdate,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    PATCH /utilisateurs/moi/profil
    ────────────────────────────────
    Tous acteurs authentifiés — Champs modifiables :
      - titre_professionnel, biographie, taux_horaire
      - disponibilite (toggle disponibilité)
      - linkedin, github, dribbble, portfolio (liens sociaux)
    Règle palier : le nombre de liens sociaux affichés dépend du palier.
    """
    profil_service = ProfilService(db)
    profil = profil_service.mettre_a_jour_profil(
        utilisateur_id=utilisateur_actuel["id"],
        titre_professionnel=donnees_profil.titre_professionnel,
        biographie=donnees_profil.biographie,
        taux_horaire=donnees_profil.taux_horaire,
        disponibilite=donnees_profil.disponibilite,
        current_user_id=utilisateur_actuel["id"],
        current_user_role=utilisateur_actuel["role"],
    )
    return profil


# ─────────────────────────────────────────────────────────────────────
# EXPÉRIENCES (FREELANCE uniquement)
# ─────────────────────────────────────────────────────────────────────

@router.get(
    "/moi/experiences",
    summary="Mes expériences professionnelles",
    description="**Écran mobile** : EcranEditionProfil (section expériences).",
)
async def obtenir_mes_experiences(
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    GET /utilisateurs/moi/experiences
    ────────────────────────────────────
    FREELANCE uniquement — Liste toutes les expériences professionnelles.
    """
    profil_service = ProfilService(db)
    return {"experiences": profil_service.obtenir_experiences(utilisateur_actuel["id"])}


@router.post(
    "/moi/experiences",
    summary="Ajouter une expérience",
    description="**Écran mobile** : EcranEditionProfil (formulaire ajout expérience).",
)
async def ajouter_experience(
    donnees: ExperienceCreate,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    POST /utilisateurs/moi/experiences
    ─────────────────────────────────────
    FREELANCE uniquement — Ajoute une expérience professionnelle au profil.
    """
    profil_service = ProfilService(db)
    return profil_service.ajouter_experience(
        utilisateur_id=utilisateur_actuel["id"],
        titre=donnees.titre,
        date_debut=donnees.date_debut,
        entreprise=donnees.entreprise,
        description=donnees.description,
        date_fin=donnees.date_fin,
        current_user_id=utilisateur_actuel["id"],
        current_user_role=utilisateur_actuel["role"],
    )


# ─────────────────────────────────────────────────────────────────────
# COMPÉTENCES (FREELANCE uniquement)
# ─────────────────────────────────────────────────────────────────────

@router.get(
    "/moi/competences",
    summary="Mes compétences",
    description="**Écran mobile** : EcranEditionProfil (section compétences).",
)
async def obtenir_mes_competences(
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    GET /utilisateurs/moi/competences
    ────────────────────────────────────
    FREELANCE uniquement — Liste toutes les compétences déclarées.
    """
    profil_service = ProfilService(db)
    return {"competences": profil_service.obtenir_competences(utilisateur_actuel["id"])}


@router.post(
    "/moi/competences",
    summary="Ajouter une compétence",
    description="**Écran mobile** : EcranEditionProfil (formulaire ajout compétence).",
)
async def ajouter_competence(
    donnees: CompetenceCreate,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    POST /utilisateurs/moi/competences
    ─────────────────────────────────────
    FREELANCE uniquement — Ajoute une compétence au profil.
    Niveaux : débutant | intermédiaire | avancé | expert.
    """
    profil_service = ProfilService(db)
    return profil_service.ajouter_competence(
        utilisateur_id=utilisateur_actuel["id"],
        nom=donnees.nom,
        niveau=donnees.niveau,
        current_user_id=utilisateur_actuel["id"],
        current_user_role=utilisateur_actuel["role"],
    )


# Rétrocompatibilité anciens endpoints
@router.get("/{id}/profile")
async def obtenir_profil_public_legacy(id: str, db: Session = Depends(obtenir_db)):
    """Alias rétrocompatible → GET /{id}/profil-public"""
    profil_service = ProfilService(db)
    profil = profil_service.obtenir_profil_public(id)
    if not profil:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return profil


@router.get("/me/profile")
async def obtenir_mon_profil_legacy(
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → GET /moi/profil"""
    profil_service = ProfilService(db)
    profil = profil_service.obtenir_mon_profil(utilisateur_actuel["id"])
    if not profil:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
    return profil


@router.patch("/me/profile")
async def mettre_a_jour_mon_profil_legacy(
    donnees_profil: ProfilUpdate,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → PATCH /moi/profil"""
    profil_service = ProfilService(db)
    return profil_service.mettre_a_jour_profil(
        utilisateur_id=utilisateur_actuel["id"],
        titre_professionnel=donnees_profil.titre_professionnel,
        biographie=donnees_profil.biographie,
        taux_horaire=donnees_profil.taux_horaire,
        disponibilite=donnees_profil.disponibilite,
        current_user_id=utilisateur_actuel["id"],
        current_user_role=utilisateur_actuel["role"],
    )
