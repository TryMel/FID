from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration de l'application avec gestion des secrets"""
    
    # Base de données
    DATABASE_URL: str = "sqlite:///./database.sqlite"
    
    # Sécurité JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 jours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Rate limiting
    RATE_LIMIT_AUTH: str = "5/minute"
    RATE_LIMIT_STANDARD: str = "100/minute"
    RATE_LIMIT_ADMIN: str = "200/minute"
    RATE_LIMIT_PUBLIC: str = "50/minute"
    
    # Uploads
    MAX_AVATAR_SIZE: int = 2 * 1024 * 1024  # 2 Mo
    ALLOWED_AVATAR_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Environnement
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
