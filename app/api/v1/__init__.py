"""
Package API v1 — Freelance Marketplace
========================================
Expose tous les APIRouter de l'API v1.

4 ACTEURS :
  - FREELANCE          : profil, portfolio, candidatures, abonnement, CV, QR code
  - CLIENT PARTICULIER : missions limitées (2 actives), avis, collaborations
  - CLIENT ENTREPRISE  : missions illimitées, accès freelances Elite
  - ADMIN              : gestion complète de la plateforme
"""
from app.api.v1.auth.router import router as auth
from app.api.v1.profil.router import router as profil
from app.api.v1.portfolio.router import router as portfolio
from app.api.v1.avis.router import router as avis
from app.api.v1.collaboration.router import router as collaboration
from app.api.v1.candidature.router import router as candidature
from app.api.v1.statistiques.router import router as statistiques
from app.api.v1.paiement.router import router as paiement
from app.api.v1.abonnement.router import router as abonnement
from app.api.v1.verification.router import router as verification
from app.api.v1.score_confiance.router import router as score_confiance
from app.api.v1.generateur_cv.router import router as generateur_cv
from app.api.v1.code_qr.router import router as code_qr
from app.api.v1.validation_sociale.router import router as validation_sociale
from app.api.v1.admin.router import router as admin
