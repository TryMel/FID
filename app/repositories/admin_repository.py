from sqlalchemy.orm import Session
from app.models import Utilisateur, Paiement, Collaboration, Verification
from typing import List, Dict, Any, Optional


class AdminRepository:
    """Repository pour l'administration - gère l'accès aux données admin"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_tous_utilisateurs(self) -> List[Utilisateur]:
        """Récupérer tous les utilisateurs"""
        return self.db.query(Utilisateur).all()
    
    def obtenir_utilisateur_par_id(self, user_id: str) -> Utilisateur:
        """Récupérer un utilisateur par son ID"""
        return self.db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    def mettre_a_jour_statut_utilisateur(self, user_id: str, statut: str) -> Optional[Utilisateur]:
        """Mettre à jour le statut d'un utilisateur"""
        utilisateur = self.obtenir_utilisateur_par_id(user_id)
        if utilisateur:
            utilisateur.statut = statut
            self.db.commit()
            self.db.refresh(utilisateur)
        return utilisateur
    
    def supprimer_utilisateur(self, user_id: str) -> bool:
        """Supprimer un utilisateur"""
        utilisateur = self.obtenir_utilisateur_par_id(user_id)
        if utilisateur:
            self.db.delete(utilisateur)
            self.db.commit()
            return True
        return False
    
    def obtenir_statistiques_tableau_de_bord(self) -> Dict[str, Any]:
        """Récupérer les statistiques du tableau de bord"""
        total_users = self.db.query(Utilisateur).count()
        active_users = self.db.query(Utilisateur).filter(Utilisateur.statut == "actif").count()
        freelance_count = self.db.query(Utilisateur).filter(Utilisateur.role == "freelance").count()
        client_count = self.db.query(Utilisateur).filter(Utilisateur.role == "client").count()
        
        total_revenue = sum(p.montant for p in self.db.query(Paiement).filter(Paiement.statut == "complete").all())
        active_projects = self.db.query(Collaboration).filter(Collaboration.statut == "en_cours").count()
        pending_verifications = self.db.query(Verification).filter(Verification.statut == "en_attente").count()
        
        return {
            "total_revenue": total_revenue,
            "active_projects": active_projects,
            "pending_verifications": pending_verifications,
            "recent_registrations": total_users
        }
