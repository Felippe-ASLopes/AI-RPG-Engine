import re
from typing import Optional
from src.domain.save_state import SaveState
from src.domain.quest import Quest
from src.domain.prompts import SystemPrompts
from src.infrastructure.logger import get_logger

logger = get_logger("QUEST_MANAGER")

class QuestManagerUseCase:
    def __init__(self, rag_adapter):
        self.rag_adapter = rag_adapter

    def _extract_tags(self, text: str) -> list[str]:
        raw_tags = re.findall(r'@([a-zA-Z0-9_]+)', text)
        return [tag.lower() for tag in dict.fromkeys(raw_tags)]

    def get_conditional_context(self, current_state: SaveState) -> str:
        if not current_state or not current_state.quest_log:
            return ""

        active_scene_tags = set([t.lower() for t in current_state.active_tags])
        relevant_quests = []

        for quest in current_state.quest_log:
            if quest.status != "ACTIVE":
                continue
            
            quest_tags = set([t.lower() for t in quest.related_tags])
            if not quest_tags or quest_tags.intersection(active_scene_tags):
                prefix = "[INTENÇÃO]" if quest.quest_type == "INTENTION" else "[OBJETIVO]"
                relevant_quests.append(f"- {prefix} {quest.description}")

        if not relevant_quests:
            return ""

        return SystemPrompts.QUEST_INJECTION_HEADER.value + "\n".join(relevant_quests)

    def execute_command(self, command: str, current_state: SaveState) -> str:
        if not current_state:
            return "[SISTEMA] Nenhuma campanha ativa."

        parts = command.strip().split()
        if len(parts) < 3:
            return "[SISTEMA] Formato inválido. Use /quest -add -intention [texto] ou /quest -complete [id]."

        root_flag = parts[1].lower()

        # FLUXO 1: ADICIONAR (-add ou -a)
        if root_flag in ["-add", "-a"]:
            sub_flag = parts[2].lower()
            q_type = "INTENTION" if sub_flag in ["-intention", "-i"] else "OBJECTIVE"
            
            description = " ".join(parts[3:])
            if not description:
                return "[SISTEMA] A descrição do objetivo não pode estar vazia."

            tags = self._extract_tags(description)
            new_quest = Quest(quest_type=q_type, description=description, related_tags=tags)
            current_state.quest_log.append(new_quest)
            
            return f"[SISTEMA] {q_type.capitalize()} adicionada com sucesso. ID: {new_quest.id}"

        # FLUXO 2: CONCLUIR (-complete ou -c) / FALHAR (-fail ou -f)
        elif root_flag in ["-complete", "-c", "-fail", "-f"]:
            target_id = parts[2]
            quest_to_resolve = next((q for q in current_state.quest_log if q.id == target_id), None)
            
            if not quest_to_resolve:
                return f"[SISTEMA] Objetivo ID '{target_id}' não encontrado."

            # CORREÇÃO: Verificando se a root_flag exata está na lista de sucesso
            status_str = "CONCLUÍDO" if root_flag in ["-complete", "-c"] else "FRACASSADO"
            
            type_label = "OBJETIVO" if quest_to_resolve.quest_type == "OBJECTIVE" else "INTENÇÃO"
            
            current_state.quest_log.remove(quest_to_resolve)
            
            memory_text = f"[{type_label} {status_str}] O personagem tinha o objetivo de: '{quest_to_resolve.description}'."
            self.rag_adapter.save_memory(memory_text, metadata={"source": "quest_log", "status": status_str})
            
            logger.info(f"Objetivo '{quest_to_resolve.description}' marcado como {status_str}.")
            return f"[SISTEMA] Objetivo '{quest_to_resolve.description}' marcado como {status_str}."

        return "[SISTEMA] Comando de quest desconhecido."