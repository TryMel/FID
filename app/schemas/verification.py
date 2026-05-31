from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):
    type: str = Field(..., pattern="^(identité|diplôme|certification|revenus)$", description="Type : identité, diplôme, certification ou revenus")


class VerificationResponse(BaseModel):
    reponse: str
    statut: str
