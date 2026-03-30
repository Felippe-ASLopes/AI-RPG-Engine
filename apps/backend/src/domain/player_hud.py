from pydantic import BaseModel, Field
import uuid

class PlayerStats(BaseModel):
    """Requisito 26.1: Atributos numéricos do jogador."""
    hp: int = 100
    max_hp: int = 100
    mana: int = 50
    max_mana: int = 50
    level: int = 1

class InventoryItem(BaseModel):
    """Requisito 26.2: Item físico no inventário."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str
    description: str = ""
    quantity: int = 1