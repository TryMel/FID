from pydantic import BaseModel, Field


class CVGenerateRequest(BaseModel):
    template_id: str = Field(..., pattern="^(moderne|classique|creatif|arabe)$", description="Template : moderne, classique, creatif ou arabe")
    langue: str = Field(default="fr", pattern="^(fr|en|ar)$", description="Langue : fr, en ou ar")
