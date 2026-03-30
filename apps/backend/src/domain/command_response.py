from pydantic import BaseModel
from typing import Optional, Any

class CommandResponse(BaseModel):
    """
    Padroniza o retorno do roteador central de comandos (Épico 37).
    """
    is_command: bool           # True se o texto começava com '/' (aborta o turno da IA)
    message: str = ""          # Feedback textual para ser exibido na interface do jogador
    new_state: Optional[Any] = None  # Contém o novo SaveState caso um /load tenha sido executado
    restored_input: str = ""   # NOVO: Texto devolvido ao HUD após um Rollback (Épico 21)
    # NOVO: Sinaliza ao controlador principal o que ele deve regerar (Épico 17)
    # Valores possíveis: "NONE", "TEXT", "IMAGE"
    regen_type: str = "NONE"