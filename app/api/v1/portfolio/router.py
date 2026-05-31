"""
Router Portfolio
=================
Gestion des projets portfolio des freelances.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranProfil (grille 4 projets)  → GET  /utilisateurs/{id}/projets
  - EcranPortfolio (liste complète) → GET  /utilisateurs/moi/projets
  - EcranPortfolio (ajout)          → POST /utilisateurs/moi/projets
  - EcranPortfolio (modif/ordre)    → PUT  /utilisateurs/moi/projets/{pid}
  - EcranPortfolio (suppression)    → DELETE /utilisateurs/moi/projets/{pid}

ACTEURS :
  FREELANCE          → CRUD complet sur ses propres projets
  CLIENT / PUBLIC    → Lecture seule
  ADMIN              → Accès complet

RÈGLES PALIER :
  GRATUIT  → max 4 projets
  PRO      → max 20 projets
  PREMIUM  → max 20 projets
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.portfolio_service import PortfolioService
from app.database import obtenir_db
from app.schemas.portfolio import ProjetCreer, ProjetMettreAJour
from app.security.auth import obtenir_utilisateur_actuel
from app.security.dependencies import exiger_freelance
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/{userId}/projets",
    summary="Projets portfolio d'un utilisateur (public)",
    description=(
        "Retourne tous les projets d'un freelance triés par ordre_affichage. "
        "**Écrans** : EcranProfil (grille 4 items) + EcranPortfolio (liste complète)."
    ),
)
async def obtenir_projets_utilisateur(
    userId: str,
    db: Session = Depends(obtenir_db),
):
    """
    GET /utilisateurs/{userId}/projets
    ────────────────────────────────────
    Tous acteurs (public) — Retourne les projets triés par ordre_affichage.
    """
    portfolio_service = PortfolioService(db)
    projets = portfolio_service.obtenir_projets_utilisateur(userId)
    return {"projets": projets, "total": len(projets)}


@router.get(
    "/moi/projets",
    summary="Mes projets portfolio",
    description="**Écran** : EcranPortfolio (vue propriétaire avec actions CRUD).",
)
async def obtenir_mes_projets(
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    GET /utilisateurs/moi/projets
    ───────────────────────────────
    FREELANCE uniquement — Retourne ses propres projets avec toutes les données.
    """
    portfolio_service = PortfolioService(db)
    projets = portfolio_service.obtenir_projets_utilisateur(utilisateur_actuel["id"])
    return {"projets": projets, "total": len(projets)}


@router.post(
    "/moi/projets",
    summary="Ajouter un projet portfolio",
    description=(
        "Crée un nouveau projet. Vérifie le quota selon le palier. "
        "**Écran** : EcranPortfolio (formulaire ajout)."
    ),
)
async def creer_projet(
    donnees: ProjetCreer,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    POST /utilisateurs/moi/projets
    ────────────────────────────────
    FREELANCE uniquement — Crée un projet.
    Règle palier : GRATUIT=4 max, PRO/PREMIUM=20 max.
    """
    portfolio_service = PortfolioService(db)
    try:
        projet = portfolio_service.creer_projet(
            utilisateur_id=utilisateur_actuel["id"],
            titre=donnees.titre,
            description=donnees.description,
            image_url=donnees.image_url,
            images_urls=donnees.images_urls,
            url_projet=donnees.url_projet,
            technologies=donnees.technologies,
            ordre_affichage=donnees.ordre_affichage or 0,
        )
        return projet
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/moi/projets/{projectId}",
    summary="Modifier un projet portfolio",
    description=(
        "Met à jour un projet existant. Utilisé aussi pour le réordonnancement (drag & drop). "
        "**Écran** : EcranPortfolio (édition + réordonnancement)."
    ),
)
async def mettre_a_jour_projet(
    projectId: str,
    donnees: ProjetMettreAJour,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    PUT /utilisateurs/moi/projets/{projectId}
    ───────────────────────────────────────────
    FREELANCE propriétaire uniquement.
    Pour le drag & drop : envoyer uniquement ordre_affichage.
    """
    portfolio_service = PortfolioService(db)
    try:
        projet = portfolio_service.mettre_a_jour_projet(
            projet_id=projectId,
            proprietaire_id=utilisateur_actuel["id"],
            titre=donnees.titre,
            description=donnees.description,
            image_url=donnees.image_url,
            images_urls=donnees.images_urls,
            url_projet=donnees.url_projet,
            technologies=donnees.technologies,
            ordre_affichage=donnees.ordre_affichage,
        )
        return projet
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete(
    "/moi/projets/{projectId}",
    summary="Supprimer un projet portfolio",
    description="**Écran** : EcranPortfolio (confirmation suppression).",
)
async def supprimer_projet(
    projectId: str,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    DELETE /utilisateurs/moi/projets/{projectId}
    ──────────────────────────────────────────────
    FREELANCE propriétaire uniquement.
    """
    portfolio_service = PortfolioService(db)
    try:
        portfolio_service.supprimer_projet(
            projet_id=projectId,
            proprietaire_id=utilisateur_actuel["id"],
        )
        return {"message": "Projet supprimé avec succès"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ── Rétrocompatibilité anciens endpoints ──────────────────────────────

@router.get("/{userId}/projects")
async def obtenir_projets_legacy(userId: str, db: Session = Depends(obtenir_db)):
    """Alias rétrocompatible → GET /{userId}/projets"""
    portfolio_service = PortfolioService(db)
    projets = portfolio_service.obtenir_projets_utilisateur(userId)
    return {"projects": projets}


@router.post("/{userId}/projects")
async def creer_projet_legacy(
    userId: str,
    donnees: ProjetCreer,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → POST /moi/projets"""
    if utilisateur_actuel["id"] != userId:
        raise HTTPException(status_code=403, detail="Vous ne pouvez créer des projets que pour votre propre compte")
    portfolio_service = PortfolioService(db)
    try:
        return portfolio_service.creer_projet(
            utilisateur_id=userId,
            titre=donnees.titre,
            description=donnees.description,
            image_url=donnees.image_url,
            images_urls=donnees.images_urls,
            url_projet=donnees.url_projet,
            technologies=donnees.technologies,
            ordre_affichage=donnees.ordre_affichage or 0,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{userId}/projects/{projectId}")
async def mettre_a_jour_projet_legacy(
    userId: str,
    projectId: str,
    donnees: ProjetMettreAJour,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → PUT /moi/projets/{projectId}"""
    portfolio_service = PortfolioService(db)
    try:
        return portfolio_service.mettre_a_jour_projet(
            projet_id=projectId,
            proprietaire_id=utilisateur_actuel["id"],
            titre=donnees.titre,
            description=donnees.description,
            image_url=donnees.image_url,
            images_urls=donnees.images_urls,
            url_projet=donnees.url_projet,
            technologies=donnees.technologies,
            ordre_affichage=donnees.ordre_affichage,
        )
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{userId}/projects/{projectId}")
async def supprimer_projet_legacy(
    userId: str,
    projectId: str,
    utilisateur_actuel: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → DELETE /moi/projets/{projectId}"""
    portfolio_service = PortfolioService(db)
    try:
        portfolio_service.supprimer_projet(projet_id=projectId, proprietaire_id=utilisateur_actuel["id"])
        return {"message": "Projet supprimé"}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
