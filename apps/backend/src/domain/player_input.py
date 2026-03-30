from pydantic import BaseModel
from typing import List

class ParsedInput(BaseModel):
    """
    Representa a jogada do usuário já mastigada e categorizada pelo sistema (Épico 8).
    """
    # Ações (>) e Falas (") na ordem em que foram digitadas
    narrative_blocks: List[str] = []
    
    # Trapaças ($) - Fatos impostos pelo jogador à IA
    system_overrides: List[str] = []
    
    # Feedbacks (#) - Correções de tom ou mecânica
    feedback_notes: List[str] = []

    # Novo campo para o Épico 10 (*)
    forced_queries: List[str] = []

    @property
    def has_content(self) -> bool:
        """Retorna True se houver qualquer tipo de dado útil no input."""
        return bool(self.narrative_blocks or self.system_overrides or self.feedback_notes)