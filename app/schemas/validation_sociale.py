from pydantic import BaseModel, Field, validator


class SocialValidationRequest(BaseModel):
    plateforme: str = Field(..., min_length=2, max_length=50, description="Plateforme (2-50 caractères)")
    url: str = Field(..., pattern=r'^https?://', description="URL doit commencer par http:// ou https://")
    
    @validator('url')
    def validate_url(cls, v):
        """Valider que l'URL est bien formée"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('L\'URL doit commencer par http:// ou https://')
        return v
