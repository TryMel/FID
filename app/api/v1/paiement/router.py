"""
Router Paiement
================
Gestion des paiements et calcul des frais de transaction.

ÉCRANS MOBILES ASSOCIÉS :
  - EcranAbonnement → POST /paiements/creer-intention
  - EcranAbonnement → POST /paiements/verifier/{paymentId}
  - EcranAbonnement → POST /paiements/calculer-frais

ACTEURS :
  FREELANCE          → Paiements d'abonnement (Pro/Premium)
  CLIENT PARTICULIER → Paiements de missions (frais de service 5% si Gratuit)
  CLIENT ENTREPRISE  → Paiements de missions (0% frais)
  ADMIN              → Consultation de tous les paiements

MODÈLE ÉCONOMIQUE :
  - Freelance Gratuit  : 5% de frais sur chaque mission
  - Freelance Pro      : 2% de frais
  - Freelance Premium  : 0% de frais
  - Abonnement Pro     : 9 500 XOF/mois
  - Abonnement Premium : 24 000 XOF/mois

DEVISE PAR PAYS (header X-Country) :
  CI → XOF | FR → EUR | US → USD | NG → NGN | KE → KES
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from app.services.paiement_service import PaiementService
from app.database import obtenir_db
from app.schemas.paiement import PaymentIntentRequest, FeeCalculationRequest
from app.security.auth import obtenir_utilisateur_actuel
from app.repositories.auth_repository import AuthRepository
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/statut-abonnement",
    summary="Statut d'abonnement de l'utilisateur connecté",
    description=(
        "Retourne le palier actif, la date d'expiration et le solde de candidatures. "
        "**Écran** : EcranAbonnement (affichage palier actuel)."
    ),
)
async def obtenir_statut_abonnement(
    request: Request,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    GET /paiements/statut-abonnement
    ──────────────────────────────────
    Tous acteurs authentifiés — Retourne :
      - statut : actif | expiré
      - palier : gratuit | pro | premium
      - date_expiration : datetime ou null
      - devise : XOF | EUR | USD selon le pays
    """
    paiement_service = PaiementService(db)
    country = getattr(request.state, "country", "CI")
    return paiement_service.obtenir_statut_abonnement(utilisateur_actuel["id"])


@router.post(
    "/creer-intention",
    summary="Créer une intention de paiement",
    description=(
        "Initie un paiement via Moneroo/Stripe. "
        "**Écran** : EcranAbonnement (bouton 'Passer au Pro/Premium')."
    ),
)
async def creer_intention_paiement(
    donnees: PaymentIntentRequest,
    request: Request,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    POST /paiements/creer-intention
    ─────────────────────────────────
    Tous acteurs authentifiés — Crée une intention de paiement.
    Retourne : client_secret, amount, currency, palier.
    """
    paiement_service = PaiementService(db)
    country = getattr(request.state, "country", "CI")
    return paiement_service.creer_intention_paiement(
        utilisateur_id=utilisateur_actuel["id"],
        montant=donnees.montant,
        palier=donnees.palier,
        country=country,
    )


@router.post(
    "/verifier/{paymentId}",
    summary="Vérifier un paiement",
    description=(
        "Vérifie le statut d'un paiement après redirection Stripe/Moneroo. "
        "**Écran** : EcranAbonnement (callback après paiement)."
    ),
)
async def verifier_paiement(
    paymentId: str,
    request: Request,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    POST /paiements/verifier/{paymentId}
    ──────────────────────────────────────
    Tous acteurs authentifiés — Vérifie et confirme un paiement.
    Retourne : status (succès | échec), payment_id.
    """
    paiement_service = PaiementService(db)
    return paiement_service.verifier_paiement(paymentId)


@router.post(
    "/calculer-frais",
    summary="Calculer les frais de transaction",
    description=(
        "Calcule les frais selon le palier du freelance et le pays. "
        "Inclut TVA locale. "
        "**Écran** : EcranAbonnement (affichage du détail des frais)."
    ),
)
async def calculer_frais(
    donnees: FeeCalculationRequest,
    request: Request,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    POST /paiements/calculer-frais
    ────────────────────────────────
    Tous acteurs authentifiés — Retourne :
      - montant_base : float
      - tva          : float
      - taux_tva     : float
      - total        : float
      - devise       : XOF | EUR | USD
    """
    paiement_service = PaiementService(db)
    country = getattr(request.state, "country", "CI")
    return paiement_service.calculer_frais(donnees.montant, country)


# Rétrocompatibilité anciens endpoints
@router.get("/subscription-status")
async def statut_abonnement_legacy(
    request: Request,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → GET /statut-abonnement"""
    paiement_service = PaiementService(db)
    return paiement_service.obtenir_statut_abonnement(utilisateur_actuel["id"])


@router.post("/create-payment-intent")
async def creer_intention_legacy(
    donnees: PaymentIntentRequest,
    request: Request,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → POST /creer-intention"""
    paiement_service = PaiementService(db)
    country = getattr(request.state, "country", "CI")
    return paiement_service.creer_intention_paiement(
        utilisateur_id=utilisateur_actuel["id"],
        montant=donnees.montant,
        palier=donnees.palier,
        country=country,
    )


@router.post("/verify-payment/{paymentId}")
async def verifier_paiement_legacy(
    paymentId: str,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → POST /verifier/{paymentId}"""
    paiement_service = PaiementService(db)
    return paiement_service.verifier_paiement(paymentId)


@router.post("/calculer-les-frais")
async def calculer_frais_legacy(
    donnees: FeeCalculationRequest,
    request: Request,
    utilisateur_actuel: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """Alias rétrocompatible → POST /calculer-frais"""
    paiement_service = PaiementService(db)
    country = getattr(request.state, "country", "CI")
    return paiement_service.calculer_frais(donnees.montant, country)
