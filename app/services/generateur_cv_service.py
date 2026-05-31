from sqlalchemy.orm import Session
from app.models import CV
from app.repositories.generateur_cv_repository import GenerateurCVRepository
from typing import Optional, List
import qrcode
from io import BytesIO
import base64

class GenerateurCVService:
    def __init__(self, db: Session):
        self.db = db
        self.cv_repo = GenerateurCVRepository(db)

    def generer_cv(self, utilisateur_id: str, template_id: str, langue: str = "fr", palier: str = "gratuit") -> CV:
        """Générer un CV"""
        # Vérifier le quota selon le palier
        if palier == "gratuit":
            raise ValueError("La génération de CV est disponible à partir du palier Pro")
        
        # Simulation de génération de CV
        cv = CV(
            utilisateur_id=utilisateur_id,
            template_id=template_id,
            contenu=f"Contenu CV template {template_id} langue {langue}",
            url_pdf=f"https://storage.example.com/cv/{utilisateur_id}.pdf"
        )
        
        return self.cv_repo.creer(cv)

    def obtenir_mon_cv(self, utilisateur_id: str) -> Optional[CV]:
        """Obtenir mon CV"""
        return self.cv_repo.obtenir_par_id_utilisateur(utilisateur_id)

    def obtenir_templates(self, langue: str = "fr") -> List[dict]:
        """Obtenir les templates de CV disponibles"""
        templates = [
            {"id": "moderne", "nom": "Moderne", "langue": langue, "rtl": False},
            {"id": "classique", "nom": "Classique", "langue": langue, "rtl": False},
            {"id": "creatif", "nom": "Creatif", "langue": langue, "rtl": False},
            {"id": "arabe", "nom": "Arabe", "langue": "ar", "rtl": True}
        ]
        
        if langue == "ar":
            return [t for t in templates if t["langue"] == "ar"]
        
        return [t for t in templates if t["langue"] != "ar"]

    def obtenir_cv(self, cv_id: str) -> Optional[CV]:
        """Obtenir un CV spécifique"""
        return self.cv_repo.obtenir_par_id(cv_id)

    def verifier_quota_cv(self, utilisateur_id: str, palier: str) -> bool:
        """Vérifier si l'utilisateur peut générer des CV selon son palier"""
        if palier == "gratuit":
            return False
        elif palier == "pro":
            return True  # 3 templates
        elif palier == "premium":
            return True  # Illimité
        return False
