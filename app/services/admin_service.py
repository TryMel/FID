from sqlalchemy.orm import Session
from app.models import Utilisateur, Collaboration, Paiement
from app.repositories.admin_repository import AdminRepository
from app.repositories.auth_repository import AuthRepository
from typing import List, Dict

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.admin_repo = AdminRepository(db)
        self.auth_repo = AuthRepository(db)

    def obtenir_statistiques_tableau_de_bord(self) -> Dict:
        """Obtenir les statistiques du tableau de bord admin"""
        return self.admin_repo.obtenir_statistiques_tableau_de_bord()

    def obtenir_tous_utilisateurs(self) -> List[Utilisateur]:
        """Obtenir tous les utilisateurs"""
        return self.admin_repo.obtenir_tous_utilisateurs()

    def obtenir_details_utilisateur(self, user_id: str):
        """Obtenir les détails d'un utilisateur"""
        return self.admin_repo.obtenir_utilisateur_par_id(user_id)

    def mettre_a_jour_statut_utilisateur(self, user_id: str, statut: str):
        """Mettre à jour le statut d'un utilisateur"""
        return self.admin_repo.mettre_a_jour_statut_utilisateur(user_id, statut)

    def supprimer_utilisateur(self, user_id: str):
        """Supprimer un utilisateur"""
        return self.admin_repo.supprimer_utilisateur(user_id)
