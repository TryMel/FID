"""
Router Collaboration (Missions)
=================================
Endpoints pour la gestion des missions publiées par les clients.

ACTEURS ET ACCÈS :
- CLIENT PARTICULIER / ENTREPRISE : créer, voir et gérer ses missions
- FREELANCE : voir la liste des missions disponibles (filtrée selon son palier)
- ADMIN : accès complet
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.collaboration_service import CollaborationService
from app.database import obtenir_db
from app.schemas.collaboration import CollaborationCreer, CollaborationMettreAJour, CollaborationReponse
from app.security.auth import obtenir_utilisateur_actuel, obtenir_utilisateur_optionnel
from app.security.dependencies import exiger_client, exiger_freelance_ou_client
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter()


@router.get("/")
async def obtenir_missions_disponibles(
    current_user: Optional[dict] = Depends(obtenir_utilisateur_optionnel),
    db: Session = Depends(obtenir_db),
):
    """
    Obtenir la liste des missions disponibles.

    - FREELANCE PREMIUM/PRO : voit toutes les missions y compris prioritaires récentes
    - FREELANCE GRATUIT : ne voit pas les missions prioritaires publiées <24h
    - CLIENT / non authentifié : voit toutes les missions (lecture publique)
    """
    collaboration_service = CollaborationService(db)

    # Déterminer le palier du freelance pour filtrer les missions prioritaires
    palier = "gratuit"
    if current_user:
        from app.repositories.auth_repository import AuthRepository
        auth_repo = AuthRepository(db)
        utilisateur = auth_repo.obtenir_par_id(current_user["id"])
        if utilisateur:
            palier = utilisateur.palier

    missions = collaboration_service.obtenir_toutes_missions(freelance_palier=palier)
    return {"missions": missions, "total": len(missions)}


@router.get("/mes-missions")
async def obtenir_mes_missions(
    current_user: dict = Depends(exiger_client),
    db: Session = Depends(obtenir_db),
):
    """
    Obtenir les missions publiées par le client connecté.
    Réservé aux clients (particulier ou entreprise).
    """
    collaboration_service = CollaborationService(db)
    missions = collaboration_service.obtenir_missions_client(current_user["id"])
    return {"missions": missions, "total": len(missions)}


@router.get("/{id}")
async def obtenir_detail_mission(
    id: str,
    current_user: Optional[dict] = Depends(obtenir_utilisateur_optionnel),
    db: Session = Depends(obtenir_db),
):
    """
    Obtenir le détail complet d'une mission.
    Inclut le nombre de candidatures (preuve sociale - Mimétisme de Girard).
    """
    collaboration_service = CollaborationService(db)
    mission = collaboration_service.obtenir_detail_mission(id)

    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")

    return mission


@router.post("/")
async def creer_mission(
    collaboration_data: CollaborationCreer,
    current_user: dict = Depends(exiger_client),
    db: Session = Depends(obtenir_db),
):
    """
    Créer une nouvelle mission.

    Règles métier :
    - CLIENT PARTICULIER : limité à 2 missions actives simultanées
    - CLIENT ENTREPRISE : illimité
    - La mission peut être marquée 'prioritaire' (visible en premier pour les freelances Pro/Premium)
    """
    collaboration_service = CollaborationService(db)

    try:
        mission = collaboration_service.creer_mission(
            client_id=current_user["id"],
            titre=collaboration_data.titre,
            description=collaboration_data.description,
            budget=collaboration_data.budget,
            date_debut=collaboration_data.date_debut,
            date_fin=collaboration_data.date_fin,
            photos=collaboration_data.photos,
            zone_intervention=collaboration_data.zone_intervention,
            limite_temps=collaboration_data.limite_temps,
            prioritaire=collaboration_data.prioritaire,
        )
        return mission
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{id}/statut")
async def mettre_a_jour_statut_mission(
    id: str,
    status_update: CollaborationMettreAJour,
    current_user: dict = Depends(exiger_client),
    db: Session = Depends(obtenir_db),
):
    """
    Mettre à jour le statut d'une mission.
    Seul le client propriétaire peut modifier le statut.
    """
    collaboration_service = CollaborationService(db)

    # Vérifier que la mission appartient au client connecté
    mission = collaboration_service.obtenir_collaboration(id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    if mission.client_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres missions")

    mission_maj = collaboration_service.mettre_a_jour_statut(id, status_update.statut)
    return mission_maj


# Rétrocompatibilité avec l'ancien endpoint
@router.put("/{id}/status")
async def mettre_a_jour_statut_collaboration_legacy(
    id: str,
    status_update: CollaborationMettreAJour,
    current_user: dict = Depends(exiger_client),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible pour PUT /{id}/statut"""
    collaboration_service = CollaborationService(db)
    mission = collaboration_service.obtenir_collaboration(id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    if mission.client_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres missions")
    return collaboration_service.mettre_a_jour_statut(id, status_update.statut)
