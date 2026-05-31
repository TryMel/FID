from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Callable


# Créer le limiter
limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handler personnalisé pour les erreurs de rate limiting"""
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Trop de requêtes. Veuillez réessayer plus tard.",
        headers={"Retry-After": str(exc.retry_after)}
    )


# Décorateurs pour différents niveaux de rate limiting
def rate_limit_auth(identifier: str):
    """Rate limiting pour l'authentification (plus strict)"""
    return limiter.limit("5/minute")(identifier)


def rate_limit_standard(identifier: str):
    """Rate limiting standard"""
    return limiter.limit("100/minute")(identifier)


def rate_limit_admin(identifier: str):
    """Rate limiting pour les routes admin (plus permissif)"""
    return limiter.limit("200/minute")(identifier)


def rate_limit_public(identifier: str):
    """Rate limiting pour les routes publiques"""
    return limiter.limit("50/minute")(identifier)
