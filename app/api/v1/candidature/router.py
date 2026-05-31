"""
Router Candidature (Postulations)
====================================
Endpoints pour la gestion des candidatures de freelances aux missions.

ACTEURS ET ACCÈS :
- FREELANCE : postuler, voir ses candidatures, booster une candidature (Pro/Premium)
- CLIENT PARTICULIER / ENTREPRISE : voir les candidatures de ses missions, accepter/refuser
- ADMIN : accès complet

LOGIQUES ÉCONOMIQUES INTÉGRÉES :
- Paradoxe de Jevons : quota de candidatures par mois (3 gratuit / 15 pro / illimité premium)
  → Force les freelances gratuits à cibler leurs candidatures avec soin
- Mimétisme social (Girard) : le nombre de candidatures est visible par le client
  → Crée une preuve sociale qui incite d'autres freelances à postuler
- Pareto 80/20 : les candidatures boostées (payantes) remontent en tête de liste
  → Les 20% de freelances qui investissent génèrent 80% de la visibilité
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.candidature_service import CandidatureService
from app.database import obtenir_db
from app.schemas.candidature import CandidatureCreer, CandidatureBooster, CandidatureStatutUpdate, CandidatureReponse
from app.security.dependencies import exiger_freelance, exiger_client, exiger_freelance_ou_client
from app.security.auth import obtenir_utilisateur_actuel
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────
# ENDPOINTS FREELANCE
# ─────────────────────────────────────────────────────────────────────

@router.post("/missions/{collaboration_id}/postuler")
async def postuler_mission(
    collaboration_id: str,
    candidature_data: CandidatureCreer,
    current_user: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    Postuler à une mission.

    Règles métier :
    - Quota mensuel : 3 (gratuit) / 15 (pro) / illimité (premium) — Paradoxe de Jevons
    - Un freelance ne peut postuler qu'une seule fois par mission
    - Les missions prioritaires sont réservées aux Pro/Premium pendant 24h
    - Le solde de candidatures est décrémenté à chaque postulation (sauf Premium)
    """
    candidature_service = CandidatureService(db)

    try:
        candidature = candidature_service.postuler(
            collaboration_id=collaboration_id,
            freelance_id=current_user["id"],
            message_motivation=candidature_data.message_motivation,
            tarif_propose=candidature_data.tarif_propose,
            duree_estimee=candidature_data.duree_estimee,
        )
        return candidature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/mes-candidatures")
async def obtenir_mes_candidatures(
    current_user: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    Obtenir toutes les candidatures soumises par le freelance connecté.
    Inclut le statut de chaque candidature (en_attente, vue, acceptée, refusée).
    """
    candidature_service = CandidatureService(db)
    candidatures = candidature_service.obtenir_mes_candidatures(current_user["id"])
    return {"candidatures": candidatures, "total": len(candidatures)}


@router.post("/{candidature_id}/booster")
async def booster_candidature(
    candidature_id: str,
    boost_data: CandidatureBooster,
    current_user: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    Booster une candidature pour qu'elle apparaisse en tête de liste chez le client.

    Fonctionnalité payante (PRO ou PREMIUM uniquement).
    Logique Mimétisme social : le client voit d'abord les candidatures boostées,
    ce qui crée un effet d'attraction et de preuve sociale.
    """
    candidature_service = CandidatureService(db)

    try:
        candidature = candidature_service.booster_candidature(
            candidature_id=candidature_id,
            freelance_id=current_user["id"],
        )
        return candidature
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/solde-candidatures")
async def obtenir_solde_candidatures(
    current_user: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    Obtenir le solde de candidatures restantes pour le mois en cours.
    Logique Paradoxe de Jevons : afficher le quota restant incite à postuler
    avec soin et crée une pression psychologique positive.
    """
    from app.repositories.auth_repository import AuthRepository
    auth_repo = AuthRepository(db)
    utilisateur = auth_repo.obtenir_par_id(current_user["id"])

    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    from app.services.candidature_service import QUOTAS_CANDIDATURES
    quota_total = QUOTAS_CANDIDATURES.get(utilisateur.palier, 3)
    solde = utilisateur.solde_candidatures if utilisateur.palier != "premium" else None

    return {
        "palier": utilisateur.palier,
        "solde_restant": solde,
        "quota_mensuel": quota_total if utilisateur.palier != "premium" else "illimité",
        "illimite": utilisateur.palier == "premium",
    }


# ─────────────────────────────────────────────────────────────────────
# ENDPOINTS CLIENT
# ─────────────────────────────────────────────────────────────────────

@router.get("/missions/{collaboration_id}/candidatures")
async def obtenir_candidatures_mission(
    collaboration_id: str,
    current_user: dict = Depends(exiger_client),
    db: Session = Depends(obtenir_db),
):
    """
    Obtenir toutes les candidatures d'une mission.

    Réservé au client propriétaire de la mission.
    Triées : candidatures boostées (payantes) en premier, puis par date.
    Inclut le total (preuve sociale - Mimétisme de Girard).
    """
    candidature_service = CandidatureService(db)

    try:
        result = candidature_service.obtenir_candidatures_mission(
            collaboration_id=collaboration_id,
            client_id=current_user["id"],
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/{candidature_id}/statut")
async def changer_statut_candidature(
    candidature_id: str,
    statut_data: CandidatureStatutUpdate,
    current_user: dict = Depends(exiger_client),
    db: Session = Depends(obtenir_db),
):
    """
    Accepter ou refuser une candidature.

    Réservé au client propriétaire de la mission.
    Si acceptée : le freelance est lié à la collaboration et la mission passe en 'en_cours'.
    """
    candidature_service = CandidatureService(db)

    try:
        candidature = candidature_service.changer_statut_candidature(
            candidature_id=candidature_id,
            nouveau_statut=statut_data.statut,
            client_id=current_user["id"],
        )
        return candidature
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
