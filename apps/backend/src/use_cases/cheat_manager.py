from src.adapters.cheat_repository import JsonCheatRepository
from src.domain.prompts import CheatPrompts
from src.infrastructure.logger import get_logger

logger = get_logger("CHEAT_MANAGER")

class CheatManagerUseCase:
    """
    Orquestra o Épico 39: Regras de Mundo e Trapaças.
    """
    def __init__(self, cheat_repository: JsonCheatRepository):
        self.cheat_repository = cheat_repository

    def add_cheat(self, cheat_text: str) -> str:
        """Adiciona uma nova regra inquestionável ao mundo."""
        cheat_text = cheat_text.strip()
        if not cheat_text:
            return "[SISTEMA] O texto da trapaça não pode estar vazio."

        cheats = self.cheat_repository.load_cheats()
        cheats.active_overrides.append(cheat_text)

        success = self.cheat_repository.save_cheats(cheats)

        if success:
            logger.warning(f"TRAPAÇA ATIVADA: '{cheat_text}'")
            return "[SISTEMA] Trapaça registrada com sucesso. As leis do mundo foram alteradas."
        else:
            return "[SISTEMA] Falha ao registrar a trapaça no sistema."

    def get_persistent_context(self) -> str:
        """Retorna o bloco de trapaças formatado para a IA obedecer cegamente."""
        cheats = self.cheat_repository.load_cheats()

        if not cheats.active_overrides:
            return ""

        lines = [f"- {override}" for override in cheats.active_overrides]
        
        final_block = CheatPrompts.PERSISTENT_CHEAT_HEADER.value + "\n".join(lines)
        
        logger.debug(f"Bloco de trapaças injetado com {len(cheats.active_overrides)} regras absolutas.")
        return final_block