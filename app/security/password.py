from passlib.context import CryptContext
from typing import Optional

# Contexte de hachage avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hacher_mot_de_passe(password: str) -> str:
    """
    Hacher un mot de passe avec bcrypt
    
    Utilisation :
        hashed = hacher_mot_de_passe("mon_mot_de_passe")
    """
    return pwd_context.hash(password)


def verifier_mot_de_passe(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifier qu'un mot de passe en clair correspond au hash
    
    Utilisation :
        if verifier_mot_de_passe("mon_mot_de_passe", hashed_password):
            # Mot de passe correct
    """
    return pwd_context.verify(plain_password, hashed_password)
