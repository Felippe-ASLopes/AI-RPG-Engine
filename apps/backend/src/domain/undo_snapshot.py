from pydantic import BaseModel
from src.domain.save_state import SaveState

class UndoSnapshot(BaseModel):
    """
    Entidade que representa um frame no tempo (Épico 11).
    Carrega o estado do mundo e a última ação do jogador para permitir 
    a reedição no frontend (Épico 21).
    """
    state: SaveState
    last_user_input: str