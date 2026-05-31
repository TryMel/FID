from sqlalchemy.orm import Session
from app.models import CodeQR
from typing import Optional


class CodeQRRepository:
    """Repository pour les codes QR - gère l'accès aux données de codes QR"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def obtenir_par_id_utilisateur(self, user_id: str) -> Optional[CodeQR]:
        """Récupérer le code QR d'un utilisateur"""
        return self.db.query(CodeQR).filter(CodeQR.utilisateur_id == user_id).first()
    
    def obtenir_par_code(self, code: str) -> Optional[CodeQR]:
        """Récupérer un code QR par son code"""
        return self.db.query(CodeQR).filter(CodeQR.code == code).first()
    
    def creer(self, code_qr: CodeQR) -> CodeQR:
        """Créer un nouveau code QR"""
        self.db.add(code_qr)
        self.db.commit()
        self.db.refresh(code_qr)
        return code_qr
    
    def mettre_a_jour(self, code_qr: CodeQR) -> CodeQR:
        """Mettre à jour un code QR"""
        self.db.commit()
        self.db.refresh(code_qr)
        return code_qr
