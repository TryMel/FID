from sqlalchemy.orm import Session
from app.models import CodeQR
from app.repositories.code_qr_repository import CodeQRRepository
from typing import Optional
import qrcode
from io import BytesIO
import base64

class CodeQRService:
    def __init__(self, db: Session):
        self.db = db
        self.qr_repo = CodeQRRepository(db)

    def generer_code_qr(self, utilisateur_id: str, palier: str = "gratuit") -> CodeQR:
        """Générer un code QR"""
        # Vérifier si le palier permet d'avoir un QR code
        if palier == "gratuit":
            raise ValueError("Le QR code est disponible à partir du palier Pro")
        
        # Générer le contenu du QR code (deep link)
        deep_link = f"https://freelanceid.app/profil/{utilisateur_id}"
        
        # Générer le QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(deep_link)
        qr.make(fit=True)
        
        # Convertir en image base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Vérifier si un QR code existe déjà
        existing_qr = self.qr_repo.obtenir_par_id_utilisateur(utilisateur_id)
        
        if existing_qr:
            existing_qr.code = deep_link
            existing_qr.actif = True
            return self.qr_repo.mettre_a_jour(existing_qr)
        
        # Créer un nouveau QR code
        code_qr = CodeQR(
            utilisateur_id=utilisateur_id,
            code=deep_link,
            actif=True
        )
        
        return self.qr_repo.creer(code_qr)

    def obtenir_mon_code_qr(self, utilisateur_id: str, palier: str = "gratuit") -> Optional[dict]:
        """Obtenir mon code QR"""
        # Vérifier si le palier permet d'avoir un QR code
        if palier == "gratuit":
            return {
                "available": False,
                "message": "Le QR code est disponible à partir du palier Pro"
            }
        
        code_qr = self.qr_repo.obtenir_par_id_utilisateur(utilisateur_id)
        
        if not code_qr:
            return {
                "available": True,
                "exists": False,
                "message": "Aucun QR code généré"
            }
        
        return {
            "available": True,
            "exists": True,
            "code": code_qr.code,
            "actif": code_qr.actif,
            "url_image": f"https://api.example.com/qr/{code_qr.id}",
            "date_creation": str(code_qr.date_creation)
        }

    def obtenir_code_qr(self, utilisateur_id: str) -> Optional[CodeQR]:
        """Obtenir le code QR d'un utilisateur"""
        return self.qr_repo.obtenir_par_id_utilisateur(utilisateur_id)
