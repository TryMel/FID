"""
Freelance Marketplace — Point d'entrée FastAPI
================================================
Backend Python/FastAPI pour la plateforme de mise en relation
freelances ↔ clients (particuliers et entreprises).

4 ACTEURS :
  FREELANCE          → Profil, portfolio, candidatures, abonnement, CV, QR code
  CLIENT PARTICULIER → Missions limitées (2 actives max), avis, collaborations
  CLIENT ENTREPRISE  → Missions illimitées, accès freelances Elite (Club 20)
  ADMIN              → Gestion complète de la plateforme

ÉCRANS MOBILES À CRÉER (par acteur) :
══════════════════════════════════════════════════════════════════════
COMMUNS (tous acteurs)
  01. EcranConnexion          POST /api/v1/auth/login
  02. EcranInscription        POST /api/v1/auth/register
  03. EcranProfil             GET  /api/v1/utilisateurs/{id}/profil-public
  04. EcranParametres         GET  /api/v1/utilisateurs/moi/profil

FREELANCE
  05. EcranEditionProfil      PATCH /api/v1/utilisateurs/moi/profil
  06. EcranPortfolio          GET/POST/PUT/DELETE /api/v1/utilisateurs/moi/projets
  07. EcranMissions           GET  /api/v1/collaborations/
  08. EcranDetailMission      GET  /api/v1/collaborations/{id}
  09. EcranMesCandidatures    GET  /api/v1/candidatures/mes-candidatures
  10. EcranStatistiques       GET  /api/v1/utilisateurs/{id}/statistiques
  11. EcranAbonnement         GET  /api/v1/abonnements/tarifs + /actuel
  12. EcranGenerateurCV       POST /api/v1/generateur-cv/generer
  13. EcranCodeQR             GET/POST /api/v1/code-qr/moi

CLIENT PARTICULIER / ENTREPRISE
  14. EcranMesMissions        GET  /api/v1/collaborations/mes-missions
  15. EcranCreerMission       POST /api/v1/collaborations/
  16. EcranCandidaturesMission GET /api/v1/candidatures/missions/{id}/candidatures
  17. EcranRechercheFreelances GET /api/v1/utilisateurs/recherche

ADMIN
  18. EcranDashboardAdmin     GET  /api/v1/admin/tableau-de-bord
  19. EcranGestionUtilisateurs GET /api/v1/admin/utilisateurs
══════════════════════════════════════════════════════════════════════
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.api.v1 import (
    auth, profil, portfolio, avis, collaboration, candidature,
    statistiques, paiement, abonnement, verification,
    score_confiance, generateur_cv, code_qr, validation_sociale, admin,
)
from app.security.jwt import middleware_jwt
from app.middleware.rate_limit import limiter
from app.config import settings

app = FastAPI(
    title="Freelance Marketplace API",
    description=(
        "API REST pour la plateforme de freelance. "
        "4 acteurs : Freelance, Client Particulier, Client Entreprise, Admin."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# ── RATE LIMITING ─────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── MIDDLEWARE JWT ────────────────────────────────────────────────────
app.middleware("http")(middleware_jwt)


@app.middleware("http")
async def ajouter_headers_localisation(request: Request, call_next):
    """Injecte la locale, le pays et la devise dans request.state."""
    request.state.locale = request.headers.get("Accept-Language", "fr-FR")
    request.state.country = request.headers.get("X-Country", "CI")
    request.state.currency = request.headers.get("X-Currency", None)
    return await call_next(request)


@app.middleware("http")
async def ajouter_headers_securite(request: Request, call_next):
    """Ajoute les headers de sécurité HTTP sur toutes les réponses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# ── ROUTERS ───────────────────────────────────────────────────────────
# Les imports du __init__.py v1 exposent directement les APIRouter.
# AUTH — Écrans 01, 02
app.include_router(auth,              prefix="/api/v1/auth",              tags=["Auth"])
# PROFIL — Écrans 03, 04, 05, 17
app.include_router(profil,            prefix="/api/v1/utilisateurs",      tags=["Profil"])
# PORTFOLIO — Écran 06
app.include_router(portfolio,         prefix="/api/v1/utilisateurs",      tags=["Portfolio"])
# AVIS — Écran 03 (section avis)
app.include_router(avis,              prefix="/api/v1/utilisateurs",      tags=["Avis"])
# STATISTIQUES — Écran 10
app.include_router(statistiques,      prefix="/api/v1/utilisateurs",      tags=["Statistiques"])
# COLLABORATIONS (MISSIONS) — Écrans 07, 08, 14, 15
app.include_router(collaboration,     prefix="/api/v1/collaborations",    tags=["Collaborations"])
# CANDIDATURES — Écrans 09, 16
app.include_router(candidature,       prefix="/api/v1/candidatures",      tags=["Candidatures"])
# ABONNEMENT — Écran 11
app.include_router(abonnement,        prefix="/api/v1/abonnements",       tags=["Abonnements"])
# PAIEMENT
app.include_router(paiement,          prefix="/api/v1/paiements",         tags=["Paiements"])
# SCORE DE CONFIANCE — Écran 03 (badge)
app.include_router(score_confiance,   prefix="/api/v1/score-confiance",   tags=["Score Confiance"])
# GENERATEUR CV — Écran 12
app.include_router(generateur_cv,     prefix="/api/v1/generateur-cv",     tags=["Generateur CV"])
# CODE QR — Écran 13
app.include_router(code_qr,           prefix="/api/v1/code-qr",           tags=["Code QR"])
# VERIFICATION
app.include_router(verification,      prefix="/api/v1/verification",      tags=["Verification"])
# VALIDATION SOCIALE
app.include_router(validation_sociale,prefix="/api/v1/validation-sociale",tags=["Validation Sociale"])
# ADMIN — Écrans 18, 19
app.include_router(admin,             prefix="/api/v1/admin",             tags=["Admin"])


@app.get("/", tags=["Santé"])
async def racine():
    """Point d'entrée — vérifie que l'API est en ligne."""
    return {"message": "Freelance Marketplace API v1.0", "docs": "/api/docs"}


@app.get("/health", tags=["Santé"])
async def sante():
    """Health check pour les load balancers et monitoring."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000, reload=True)
