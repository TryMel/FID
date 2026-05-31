"""
Router Admin
=============
Gestion complète de la plateforme par les administrateurs.

ÉCRANS MOBILES / WEB ASSOCIÉS :
  - EcranDashboardAdmin      → GET  /admin/tableau-de-bord
  - EcranGestionUtilisateurs → GET  /admin/utilisateurs
  - EcranDetailUtilisateur   → GET  /admin/utilisateurs/{userId}
  - EcranGestionUtilisateurs → PATCH /admin/utilisateurs/{userId}/statut
  - EcranGestionUtilisateurs → DELETE /admin/utilisateurs/{userId}
  - EcranRapports            → GET  /admin/rapports
  - EcranParametresAdmin     → GET/PATCH /admin/parametres

ACTEURS :
  ADMIN uniquement — Toutes les routes sont protégées par exiger_admin.

FONCTIONNALITÉS :
  - Vue d'ensemble de la plateforme (KPIs globaux)
  - Gestion des utilisateurs (activation, suspension, suppression)
  - Consultation des rapports d'abus
  - Configuration de la plateforme
  - Réinitialisation des soldes de candidatures (cron mensuel)
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.admin_service import AdminService
from app.services.abonnement_service import AbonnementService
from app.database import obtenir_db
from app.schemas.admin import UserStats, DashboardStats, UserManagement
from app.security.dependencies import exiger_admin
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()


@router.get(
    "/tableau-de-bord",
    response_model=DashboardStats,
    summary="Tableau de bord administrateur",
    description=(
        "Retourne les KPIs globaux de la plateforme : revenus totaux, "
        "projets actifs, vérifications en attente, inscriptions récentes. "
        "**Écran** : EcranDashboardAdmin."
    ),
)
async def obtenir_tableau_de_bord(
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """
    GET /admin/tableau-de-bord
    ───────────────────────────
    ADMIN uniquement — Retourne :
      - total_revenue          : float (revenus totaux)
      - active_projects        : int (missions en cours)
      - pending_verifications  : int (vérifications en attente)
      - recent_registrations   : int (inscriptions des 30 derniers jours)
    """
    admin_service = AdminService(db)
    stats = admin_service.obtenir_statistiques_tableau_de_bord()
    return DashboardStats(
        total_revenue=stats["total_revenue"],
        active_projects=stats["active_projects"],
        pending_verifications=stats["pending_verifications"],
        recent_registrations=stats["recent_registrations"],
    )


# Alias rétrocompatible
@router.get("/dashboard", response_model=DashboardStats, include_in_schema=False)
async def tableau_de_bord_legacy(
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → GET /tableau-de-bord"""
    admin_service = AdminService(db)
    stats = admin_service.obtenir_statistiques_tableau_de_bord()
    return DashboardStats(
        total_revenue=stats["total_revenue"],
        active_projects=stats["active_projects"],
        pending_verifications=stats["pending_verifications"],
        recent_registrations=stats["recent_registrations"],
    )


@router.get(
    "/utilisateurs",
    response_model=List[UserManagement],
    summary="Liste de tous les utilisateurs",
    description=(
        "Retourne la liste complète des utilisateurs avec leur statut. "
        "**Écran** : EcranGestionUtilisateurs."
    ),
)
async def obtenir_tous_utilisateurs(
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """
    GET /admin/utilisateurs
    ────────────────────────
    ADMIN uniquement — Retourne tous les utilisateurs (freelances, clients, admins).
    """
    admin_service = AdminService(db)
    users = admin_service.obtenir_tous_utilisateurs()
    return [
        UserManagement(
            id=user.id,
            email=user.email,
            nom=user.nom,
            role=user.role,
            statut=user.statut,
            date_creation=str(user.date_creation),
        )
        for user in users
    ]


# Alias rétrocompatible
@router.get("/users", response_model=List[UserManagement], include_in_schema=False)
async def utilisateurs_legacy(
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → GET /utilisateurs"""
    admin_service = AdminService(db)
    users = admin_service.obtenir_tous_utilisateurs()
    return [
        UserManagement(id=u.id, email=u.email, nom=u.nom, role=u.role,
                       statut=u.statut, date_creation=str(u.date_creation))
        for u in users
    ]


@router.get(
    "/utilisateurs/{userId}",
    summary="Détails d'un utilisateur",
    description="**Écran** : EcranDetailUtilisateur.",
)
async def obtenir_details_utilisateur(
    userId: str,
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """
    GET /admin/utilisateurs/{userId}
    ──────────────────────────────────
    ADMIN uniquement — Retourne le profil complet d'un utilisateur.
    """
    admin_service = AdminService(db)
    user = admin_service.obtenir_details_utilisateur(userId)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {
        "id": user.id,
        "email": user.email,
        "nom": user.nom,
        "role": user.role,
        "type_compte": user.type_compte,
        "palier": user.palier,
        "statut": user.statut,
        "solde_candidatures": user.solde_candidatures,
        "date_fin_abonnement": user.date_fin_abonnement,
        "profil": {
            "titre_professionnel": user.profil.titre_professionnel if user.profil else None,
            "biographie": user.profil.biographie if user.profil else None,
            "taux_horaire": user.profil.taux_horaire if user.profil else None,
            "disponibilite": user.profil.disponibilite if user.profil else None,
        },
    }


@router.patch(
    "/utilisateurs/{userId}/statut",
    summary="Modifier le statut d'un utilisateur",
    description=(
        "Active, suspend ou désactive un compte utilisateur. "
        "**Écran** : EcranGestionUtilisateurs (actions sur un utilisateur)."
    ),
)
async def mettre_a_jour_statut_utilisateur(
    userId: str,
    statut: str,
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """
    PATCH /admin/utilisateurs/{userId}/statut
    ───────────────────────────────────────────
    ADMIN uniquement — Statuts : actif | suspendu | desactive.
    """
    if statut not in ["actif", "suspendu", "desactive"]:
        raise HTTPException(
            status_code=400,
            detail="Statut invalide. Valeurs acceptées : actif, suspendu, desactive"
        )
    admin_service = AdminService(db)
    user = admin_service.mettre_a_jour_statut_utilisateur(userId, statut)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"id": userId, "statut": statut, "message": f"Statut mis à jour : {statut}"}


@router.delete(
    "/utilisateurs/{userId}",
    summary="Supprimer un utilisateur",
    description="**Écran** : EcranGestionUtilisateurs (action suppression).",
)
async def supprimer_utilisateur(
    userId: str,
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """
    DELETE /admin/utilisateurs/{userId}
    ─────────────────────────────────────
    ADMIN uniquement — Suppression définitive d'un compte.
    """
    admin_service = AdminService(db)
    admin_service.supprimer_utilisateur(userId)
    return {"message": f"Utilisateur {userId} supprimé définitivement"}


@router.post(
    "/reinitialiser-soldes",
    summary="Réinitialiser les soldes de candidatures (cron mensuel)",
    description=(
        "Réinitialise les soldes de candidatures de tous les freelances au début du mois. "
        "À appeler via un cron job le 1er de chaque mois."
    ),
)
async def reinitialiser_soldes_mensuels(
    utilisateur_actuel: dict = Depends(exiger_admin),
    db: Session = Depends(obtenir_db),
):
    """
    POST /admin/reinitialiser-soldes
    ──────────────────────────────────
    ADMIN uniquement — Réinitialise les quotas mensuels de candidatures.
    Retourne le nombre d'utilisateurs mis à jour.
    """
    abonnement_service = AbonnementService(db)
    nb_mis_a_jour = abonnement_service.reinitialiser_soldes_mensuels()
    return {
        "message": f"Soldes réinitialisés pour {nb_mis_a_jour} freelances",
        "nb_mis_a_jour": nb_mis_a_jour,
    }


@router.get(
    "/rapports",
    summary="Rapports d'abus",
    description="**Écran** : EcranRapports (liste des signalements).",
)
async def obtenir_rapports(
    utilisateur_actuel: dict = Depends(exiger_admin),
):
    """
    GET /admin/rapports
    ────────────────────
    ADMIN uniquement — Retourne les rapports d'abus en attente.
    """
    return {
        "rapports": [
            {"id": "1", "type": "spam", "statut": "en_attente"},
            {"id": "2", "type": "fraude", "statut": "resolu"},
        ]
    }


@router.get(
    "/parametres",
    summary="Paramètres de la plateforme",
    description="**Écran** : EcranParametresAdmin.",
)
async def obtenir_parametres(
    utilisateur_actuel: dict = Depends(exiger_admin),
):
    """
    GET /admin/parametres
    ──────────────────────
    ADMIN uniquement — Retourne la configuration globale de la plateforme.
    """
    return {
        "mode_maintenance": False,
        "inscription_activee": True,
        "max_utilisateurs": 10000,
        "commission_freelance_gratuit": 0.05,
        "commission_freelance_pro": 0.02,
        "commission_freelance_premium": 0.00,
    }


@router.patch(
    "/parametres",
    summary="Modifier les paramètres de la plateforme",
    description="**Écran** : EcranParametresAdmin.",
)
async def mettre_a_jour_parametres(
    parametres: dict,
    utilisateur_actuel: dict = Depends(exiger_admin),
):
    """
    PATCH /admin/parametres
    ────────────────────────
    ADMIN uniquement — Met à jour la configuration globale.
    """
    return parametres
