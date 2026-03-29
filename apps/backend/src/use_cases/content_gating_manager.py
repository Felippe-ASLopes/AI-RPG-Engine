import re
from typing import Tuple
from src.domain.campaign_setup import ContentGating
from src.domain.prompts import ConstraintPrompts
from src.infrastructure.logger import get_logger

logger = get_logger("CONTENT_GATING")

class ContentGatingUseCase:
    """
    Implementa o Épico 25: Controle de Temas, Blacklist e Geração de Restrições.
    """

    def build_system_constraints(self, gating: ContentGating) -> str:
        """
        Gera o bloco de texto que será anexado ao System Prompt da LLM (Requisito 25.3).
        Se tudo for permitido, retorna uma string vazia para poupar tokens.
        """
        constraints = []

        if not gating.allow_nsfw:
            constraints.append(ConstraintPrompts.NO_NSFW.value)
            
        if not gating.allow_gore:
            constraints.append(ConstraintPrompts.NO_GORE.value)
            
        if gating.banned_topics:
            topics_str = ", ".join(gating.banned_topics)
            constraints.append(ConstraintPrompts.BANNED_TOPICS.value.format(topics=topics_str))

        if not constraints:
            return ""

        # Monta o cabeçalho e as restrições
        final_block = ConstraintPrompts.BASE_HEADER.value + "".join(constraints)
        return final_block

    def validate_llm_output(self, generated_text: str, gating: ContentGating) -> Tuple[bool, str]:
        """
        Sanity Check (Requisito 25.2). 
        Analisa a resposta recém-gerada pela LLM. Se contiver uma palavra/tema da blacklist,
        retorna False e a palavra que causou a violação, para que o motor dispare o regen silencioso.
        """
        if not gating.banned_topics:
            return True, ""

        # Converte o texto para minúsculas para facilitar o match
        text_lower = generated_text.lower()

        for topic in gating.banned_topics:
            topic_lower = topic.lower().strip()
            
            # Usamos regex com word boundaries (\b) para evitar falsos positivos
            # Exemplo: banir "dor" não deve bloquear a palavra "dormir"
            pattern = rf"\b{re.escape(topic_lower)}\b"
            
            if re.search(pattern, text_lower):
                logger.warning(f"GATING TRIGGER: A IA gerou conteúdo banido ('{topic}'). Regeneração necessária.")
                return False, topic

        return True, ""