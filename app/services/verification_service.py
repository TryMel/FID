from sqlalchemy.orm import Session
from app.models import Verification
from app.repositories.verification_repository import VerificationRepository
from typing import Optional
from datetime import datetime, timedelta
import random
import string

class VerificationService:
    def __init__(self, db: Session):
        self.db = db
        self.verification_repo = VerificationRepository(db)

    def demander_verification(self, utilisateur_id: str, type_verification: str, country: str = "CI") -> Verification:
        """Demander une vérification"""
        code = self.generer_code_verification()
        date_expiration = datetime.now() + timedelta(hours=24)
        
        verification = Verification(
            utilisateur_id=utilisateur_id,
            type=type_verification,
            code=code,
            statut="en_attente",
            date_expiration=date_expiration
        )
        
        return self.verification_repo.creer(verification)

    def repondre_verification(self, verification_id: str, reponse: str, statut: str) -> Verification:
        """Répondre à une vérification (admin)"""
        return self.verification_repo.mettre_a_jour_statut(verification_id, statut)

    def obtenir_statut_verification(self, utilisateur_id: str) -> Optional[Verification]:
        """Obtenir le statut de vérification d'un utilisateur"""
        verifications = self.verification_repo.obtenir_par_id_utilisateur(utilisateur_id)
        # Retourner la première vérification en attente
        for v in verifications:
            if v.statut == "en_attente":
                return v
        return None

    def obtenir_verification_par_code(self, code: str) -> Optional[Verification]:
        """Obtenir une vérification par code"""
        return self.verification_repo.obtenir_par_code(code)

    def generer_code_verification(self) -> str:
        """Générer un code de vérification"""
        return ''.join(random.choices(string.digits, k=6))

    def obtenir_documents_requis_pour_pays(self, country: str) -> list:
        """Obtenir les documents requis pour la vérification selon le pays"""
        documents_map = {
            "CI": ["Carte d'identité nationale", "NIF", "Justificatif de domicile"],
            "FR": ["Carte d'identité", "Justificatif de domicile"],
            "US": ["Driver's License", "Social Security Number"],
            "NG": ["National ID", "BVN", "Utility Bill"],
            "KE": ["National ID", "KRA PIN", "Utility Bill"]
        }
        return documents_map.get(country, ["Document d'identité"])

    def obtenir_periode_conservation_pour_pays(self, country: str) -> int:
        """Obtenir la durée de conservation des données selon le pays (en années)"""
        retention_map = {
            "CI": 5,
            "FR": 5,
            "US": 7,
            "NG": 7,
            "KE": 7
        }
        return retention_map.get(country, 5)
