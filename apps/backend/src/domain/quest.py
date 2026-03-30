from pydantic import BaseModel, Field
from typing import List
import uuid

class Quest(BaseModel):
    """Representa uma intenção ou objetivo do jogador (Épicos 27 e 28)."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    quest_type: str  # "INTENTION" (Curto prazo) ou "OBJECTIVE" (Longo prazo)
    description: str # Requisito 27.2: Deve ser escrito na visão subjetiva do personagem
    related_tags: List[str] = [] # Requisito 27.3: Tags que ativam a injeção deste objetivo
    status: str = "ACTIVE" # "ACTIVE", "COMPLETED", "FAILED"