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

    # NOVO: Épico 32 - Consultas ao Mestre (?)
    oracle_queries: List[str] = []

    @property
    def has_content(self) -> bool:
        return bool(self.narrative_blocks or self.system_overrides or self.feedback_notes or self.oracle_queries)

class PlayerPreferences(BaseModel):
    """
    Épico 7: Entidade que armazena as preferências globais do jogador
    para tom narrativo e mecânicas do RPG.
    """
    tone_corrections: List[str] = []
    mechanic_rules: List[str] = []

class ActiveCheats(BaseModel):
    """
    Épico 39: Entidade que armazena fatos absolutos ou "trapaças"
    impostas pelo jogador para alterar as regras do mundo.
    """
    active_overrides: List[str] = []