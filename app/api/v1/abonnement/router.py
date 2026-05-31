"""
Router Abonnement (Souscriptions)
====================================
Endpoints pour la gestion des abonnements freelance.

PALIERS :
- GRATUIT (0 XOF/mois) : 3 candidatures/mois, 4 projets portfolio, 1 lien social
- PRO (~9 500 XOF/mois) : 15 candidatures/mois, 20 projets, 5 liens, CV, QR code, score confiance
- PREMIUM (~24 000 XOF/mois) : illimité, missions prioritaires 24h avant, boost candidatures, badge doré

LOGIQUES ÉCONOMIQUES :
- Freemium : le palier gratuit est suffisant pour démarrer mais crée une frustration calculée
- Jevons : les quotas de candidatures poussent naturellement vers l'upgrade
- Mimétisme : le badge Pro/Premium visible sur le profil crée une pression sociale d'upgrade
- Pareto : les 20% de freelances Premium génèrent 80% des revenus de la plateforme
"""
from fastapi import APIRouter, HTTPException, Depends
from app.services.abonnement_service import AbonnementService
from app.database import obtenir_db
from app.schemas.abonnement import AbonnementCheckout, AbonnementMettreAJour, ConfirmationEmailAbonnement
from app.security.dependencies import exiger_freelance
from app.security.auth import obtenir_utilisateur_actuel
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/actuel")
async def obtenir_abonnement_actuel(
    current_user: dict = Depends(obtenir_utilisateur_actuel),
    db: Session = Depends(obtenir_db),
):
    """
    Obtenir l'abonnement actif de l'utilisateur connecté.
    Retourne le palier, la date de début et la date d'expiration.
    """
    abonnement_service = AbonnementService(db)
    return abonnement_service.obtenir_abonnement_actuel(current_user["id"])


@router.post("/checkout")
async def initier_checkout(
    checkout_data: AbonnementCheckout,
    current_user: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    Initier le flux de paiement pour souscrire à un palier payant.
    Retourne une URL de paiement (Stripe Checkout ou Moneroo).

    Règle : seuls les freelances peuvent souscrire à un abonnement.
    """
    abonnement_service = AbonnementService(db)

    try:
        result = abonnement_service.initier_checkout(
            utilisateur_id=current_user["id"],
            palier=checkout_data.palier,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/actuel")
async def mettre_a_jour_abonnement(
    update_data: AbonnementMettreAJour,
    current_user: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    Mettre à jour l'abonnement après confirmation du paiement.
    Appelé par le frontend après redirection Stripe/Moneroo.
    """
    abonnement_service = AbonnementService(db)

    try:
        result = abonnement_service.activer_abonnement(
            utilisateur_id=current_user["id"],
            palier=update_data.palier,
            reference_paiement=update_data.reference_paiement,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirmer-email")
async def envoyer_email_confirmation(
    confirm_data: ConfirmationEmailAbonnement,
    current_user: dict = Depends(exiger_freelance),
    db: Session = Depends(obtenir_db),
):
    """
    Envoyer un email de confirmation d'abonnement.
    Appelé après activation réussie d'un palier payant.
    """
    abonnement_service = AbonnementService(db)
    return abonnement_service.envoyer_confirmation_email(
        utilisateur_id=current_user["id"],
        palier=confirm_data.palier,
        date_effet=confirm_data.date_effet,
    )


@router.get("/tarifs")
async def obtenir_tarifs():
    """
    Obtenir les tarifs des différents paliers.
    Route publique — pas d'authentification requise.
    """
    return {
        "paliers": [
            {
                "id": "gratuit",
                "nom": "Gratuit",
                "prix_mensuel_xof": 0,
                "prix_annuel_xof": 0,
                "fonctionnalites": [
                    "3 candidatures/mois",
                    "4 projets portfolio",
                    "1 lien social",
                    "Profil de base",
                ],
                "restrictions": [
                    "Pas d'accès aux missions prioritaires (24h de délai)",
                    "Score de confiance masqué",
                    "Pas de QR code",
                    "Pas de génération de CV",
                ],
            },
            {
                "id": "pro",
                "nom": "Pro",
                "prix_mensuel_xof": 9500,
                "prix_annuel_xof": 91200,  # 9500 * 12 * 0.8
                "badge_couleur": "#8DC63F",
                "fonctionnalites": [
                    "15 candidatures/mois",
                    "20 projets portfolio",
                    "5 liens sociaux",
                    "Score de confiance visible",
                    "QR code professionnel",
                    "Génération CV (3 templates)",
                    "Statistiques avancées",
                    "Badge Pro vert",
                ],
            },
            {
                "id": "premium",
                "nom": "Premium",
                "prix_mensuel_xof": 24000,
                "prix_annuel_xof": 230400,  # 24000 * 12 * 0.8
                "badge_couleur": "#FFD700",
                "fonctionnalites": [
                    "Candidatures illimitées",
                    "20 projets portfolio",
                    "5 liens sociaux",
                    "Accès missions prioritaires 24h avant les autres",
                    "Boost de candidatures (remonte en tête de liste)",
                    "Profil mis en avant dans les recherches",
                    "Score de confiance visible",
                    "QR code professionnel",
                    "CV illimités",
                    "Statistiques temps réel",
                    "Badge Premium doré",
                    "Support prioritaire",
                ],
            },
        ]
    }
