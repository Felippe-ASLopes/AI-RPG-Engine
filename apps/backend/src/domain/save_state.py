from pydantic import BaseModel
from typing import List

class SaveState(BaseModel):
    """
    Entidade pura que representa o Buffer de Contexto no momento do salvamento (Épico 12).
    """
    campaign_name: str
    context_buffer: List[str]
    active_tags: List[str]