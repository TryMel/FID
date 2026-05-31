"""
Service Abonnement
====================
Logique métier pour la gestion des souscriptions freelance.

PALIERS ET QUOTAS :
─────────────────────────────────────────────────────────────────────
GRATUIT  → 0 XOF/mois  | 3 candidatures/mois | 4 projets | 1 lien social
PRO      → 9 500 XOF/mois | 15 candidatures/mois | 20 projets | 5 liens
PREMIUM  → 24 000 XOF/mois | illimité | missions prioritaires 24h avant

LOGIQUES ÉCONOMIQUES :
- Freemium : le gratuit est fonctionnel mais crée une frustration calculée
- Jevons : les quotas de candidatures poussent naturellement vers l'upgrade
- Mimétisme : le badge visible sur le profil crée une pression sociale
- Pareto : les 20% de freelances Premium génèrent 80% des revenus
─────────────────────────────────────────────────────────────────────
"""
import uuid
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Dict

from app.repositories.auth_repository import AuthRepository
from app.repositories.paiement_repository import PaiementRepository
from app.models.paiement import Paiement
from app.models.utilisateur import Utilisateur


# Quotas de candidatures par palier (Paradoxe de Jevons)
QUOTAS_CANDIDATURES = {
    "gratuit": 3,
    "pro": 15,
    "premium": 9999,  # Illimité en pratique
}

# Durée des abonnements en jours
DUREE_ABONNEMENT_JOURS = 30

# Prix en XOF
PRIX_PALIERS = {
    "pro": 9500,
    "premium": 24000,
}


class AbonnementService:
    """Service de gestion des abonnements freelance"""

    def __init__(self, db: Session):
        self.db = db
        self.auth_repo = AuthRepository(db)
        self.paiement_repo = PaiementRepository(db)

    def obtenir_abonnement_actuel(self, utilisateur_id: str) -> Dict:
        """
        Obtenir l'abonnement actif d'un utilisateur.
        Vérifie si l'abonnement est expiré et rétrograde si nécessaire.
        """
        utilisateur = self.auth_repo.obtenir_par_id(utilisateur_id)
        if not utilisateur:
            raise ValueError("Utilisateur non trouvé")

        # Vérifier l'expiration de l'abonnement
        est_actif = True
        if utilisateur.palier != "gratuit" and utilisateur.date_fin_abonnement:
            if datetime.utcnow() > utilisateur.date_fin_abonnement.replace(tzinfo=None):
                # Abonnement expiré → rétrograder vers gratuit
                self._retrograder_vers_gratuit(utilisateur)
                est_actif = False

        solde = utilisateur.solde_candidatures if utilisateur.palier != "premium" else None

        return {
            "palier": utilisateur.palier,
            "date_debut": None,  # À enrichir avec un modèle Abonnement dédié si besoin
            "date_expiration": utilisateur.date_fin_abonnement,
            "est_actif": est_actif,
            "solde_candidatures": solde,
            "quota_mensuel": QUOTAS_CANDIDATURES.get(utilisateur.palier, 3),
            "illimite": utilisateur.palier == "premium",
            "renouvellement_automatique": utilisateur.palier != "gratuit",
        }

    def initier_checkout(self, utilisateur_id: str, palier: str) -> Dict:
        """
        Initier le flux de paiement pour un palier payant.
        Retourne une URL de paiement (Moneroo/Stripe).

        En production : intégrer l'API Moneroo ou Stripe Checkout.
        """
        utilisateur = self.auth_repo.obtenir_par_id(utilisateur_id)
        if not utilisateur:
            raise ValueError("Utilisateur non trouvé")
        if utilisateur.role != "freelance":
            raise ValueError("Seuls les freelances peuvent souscrire à un abonnement")
        if palier not in ["pro", "premium"]:
            raise ValueError("Palier invalide. Choisissez 'pro' ou 'premium'")
        if utilisateur.palier == palier:
            raise ValueError(f"Vous êtes déjà sur le palier {palier}")

        montant = PRIX_PALIERS[palier]
        reference = str(uuid.uuid4())

        # Créer un enregistrement de paiement en attente
        paiement = Paiement(
            id=reference,
            utilisateur_id=utilisateur_id,
            montant=montant,
            statut="en_attente",
            type=f"abonnement_{palier}",
            reference=reference,
        )
        self.paiement_repo.creer(paiement)

        # En production : appeler l'API Moneroo/Stripe ici
        # Pour l'instant : retourner une URL simulée avec la référence
        return {
            "checkout_url": f"https://pay.moneroo.io/checkout/{reference}",
            "reference_paiement": reference,
            "montant": montant,
            "devise": "XOF",
            "palier": palier,
            "message": "Redirigez l'utilisateur vers checkout_url pour finaliser le paiement",
        }

    def activer_abonnement(
        self,
        utilisateur_id: str,
        palier: str,
        reference_paiement: Optional[str] = None,
    ) -> Dict:
        """
        Activer un abonnement après confirmation du paiement.
        Met à jour le palier, la date d'expiration et le quota de candidatures.
        """
        utilisateur = self.auth_repo.obtenir_par_id(utilisateur_id)
        if not utilisateur:
            raise ValueError("Utilisateur non trouvé")

        # Mettre à jour le palier
        ancien_palier = utilisateur.palier
        utilisateur.palier = palier
        utilisateur.date_fin_abonnement = datetime.utcnow() + timedelta(days=DUREE_ABONNEMENT_JOURS)

        # Réinitialiser le quota de candidatures selon le nouveau palier
        utilisateur.solde_candidatures = QUOTAS_CANDIDATURES.get(palier, 3)

        # Mettre à jour le statut du paiement si une référence est fournie
        if reference_paiement:
            paiement = self.paiement_repo.obtenir_par_id(reference_paiement)
            if paiement:
                paiement.statut = "confirme"
                self.db.commit()

        self.db.commit()
        self.db.refresh(utilisateur)

        return {
            "succes": True,
            "palier": utilisateur.palier,
            "ancien_palier": ancien_palier,
            "date_expiration": utilisateur.date_fin_abonnement,
            "solde_candidatures": utilisateur.solde_candidatures,
            "message": f"Abonnement {palier} activé avec succès",
        }

    def envoyer_confirmation_email(
        self,
        utilisateur_id: str,
        palier: str,
        date_effet: str,
    ) -> Dict:
        """
        Envoyer un email de confirmation d'abonnement.
        En production : intégrer un service d'email (SendGrid, Mailgun, etc.)
        """
        utilisateur = self.auth_repo.obtenir_par_id(utilisateur_id)
        if not utilisateur:
            raise ValueError("Utilisateur non trouvé")

        # En production : envoyer un vrai email ici
        # Pour l'instant : simuler l'envoi
        return {
            "succes": True,
            "email_destinataire": utilisateur.email,
            "palier": palier,
            "date_effet": date_effet,
            "message": f"Email de confirmation envoyé à {utilisateur.email}",
        }

    def _retrograder_vers_gratuit(self, utilisateur: Utilisateur) -> None:
        """
        Rétrograder un utilisateur vers le palier gratuit.
        Appelé automatiquement quand l'abonnement expire.
        """
        utilisateur.palier = "gratuit"
        utilisateur.date_fin_abonnement = None
        utilisateur.solde_candidatures = QUOTAS_CANDIDATURES["gratuit"]
        self.db.commit()

    def reinitialiser_soldes_mensuels(self) -> int:
        """
        Réinitialiser les soldes de candidatures au début d'un nouveau mois.
        À appeler via un script cron le 1er de chaque mois.
        Retourne le nombre d'utilisateurs mis à jour.
        """
        utilisateurs = self.db.query(Utilisateur).filter(
            Utilisateur.role == "freelance",
            Utilisateur.statut == "actif",
        ).all()

        count = 0
        for utilisateur in utilisateurs:
            quota = QUOTAS_CANDIDATURES.get(utilisateur.palier, 3)
            if utilisateur.palier != "premium":
                utilisateur.solde_candidatures = quota
                count += 1

        self.db.commit()
        return count
