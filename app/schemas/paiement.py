from pydantic import BaseModel, Field


class PaymentIntentRequest(BaseModel):
    montant: float = Field(..., ge=1, le=1000000, description="Montant entre 1 et 1 000 000")
    palier: str = Field(..., pattern="^(gratuit|pro|premium)$", description="Palier : gratuit, pro ou premium")


class FeeCalculationRequest(BaseModel):
    montant: float = Field(..., ge=0, le=1000000, description="Montant entre 0 et 1 000 000")
