from src.adapters.preferences_repository import JsonPreferencesRepository
from src.domain.prompts import FeedbackPrompts
from src.infrastructure.logger import get_logger

logger = get_logger("FEEDBACK_MANAGER")

class FeedbackManagerUseCase:
    """
    Orquestra o Épico 7: Sistema de Feedback e Correção Contínua.
    """
    def __init__(self, preferences_repository: JsonPreferencesRepository):
        self.preferences_repository = preferences_repository

    def add_feedback(self, note: str, category: str = "tone") -> str:
        """
        Adiciona uma nova regra ou correção às preferências do jogador.
        :param category: "tone" (Tom Narrativo) ou "mechanic" (Regras de Jogo)
        """
        note = note.strip()
        if not note:
            return "[SISTEMA] A nota de feedback não pode estar vazia."

        prefs = self.preferences_repository.load_preferences()

        if category == "mechanic":
            prefs.mechanic_rules.append(note)
            log_type = "Mecânica"
        else:
            prefs.tone_corrections.append(note)
            log_type = "Tom"

        success = self.preferences_repository.save_preferences(prefs)

        if success:
            logger.info(f"Feedback de {log_type} adicionado: '{note}'")
            return f"[SISTEMA] Preferência de {log_type} registrada com sucesso. A IA tentará obedecer a partir de agora."
        else:
            return "[SISTEMA] Falha ao registrar a preferência."

    def get_persistent_context(self) -> str:
        """
        Tarefa 7.2: Retorna o bloco massivo de texto formatado que será 
        injetado silenciosamente no topo do contexto (System Prompt) da LLM.
        """
        prefs = self.preferences_repository.load_preferences()

        # Se o jogador nunca deu feedback, retorna string vazia para economizar tokens (8GB VRAM)
        if not prefs.tone_corrections and not prefs.mechanic_rules:
            return ""

        lines = []
        
        if prefs.tone_corrections:
            lines.append("Correções de Tom Narrativo:")
            lines.extend([f"- {note}" for note in prefs.tone_corrections])
            lines.append("") # Quebra de linha

        if prefs.mechanic_rules:
            lines.append("Regras e Mecânicas:")
            lines.extend([f"- {note}" for note in prefs.mechanic_rules])

        # Encapsula com a diretiva prioritária do domínio
        final_block = FeedbackPrompts.PERSISTENT_FEEDBACK_HEADER.value + "\n".join(lines)
        
        logger.debug(f"Bloco de preferências injetado ({len(prefs.tone_corrections)} tons, {len(prefs.mechanic_rules)} regras).")
        return final_block