import re
from typing import List
from src.domain.player_input import ParsedInput
from src.domain.prompts import SystemPrompts
from src.infrastructure.logger import get_logger

logger = get_logger("ENTITY_TAGGING")

class EntityTaggingUseCase:
    """
    Implementa o Épico 9: Sistema de Tagging de Entidades (@Mapping).
    Garante que a LLM tenha a "ficha" exata dos elementos mencionados no turno.
    """
    def __init__(self, asset_bridge, rag_adapter):
        self.asset_bridge = asset_bridge
        self.rag_adapter = rag_adapter

    def _extract_unique_tags(self, text: str) -> List[str]:
        """
        Deteta o uso do caratere @ seguido de texto alfanumérico e underscores.
        Remove duplicados mantendo a ordem para evitar processamento redundante.
        """
        raw_tags = re.findall(r'@([a-zA-Z0-9_]+)', text)
        return list(dict.fromkeys(raw_tags))

    def process_tags(self, parsed_input: ParsedInput) -> str:
        """
        Gera o bloco de texto massivo que será injetado no System Prompt.
        """
        # Junta todas as narrativas para procurar tags num lugar só
        full_narrative = " ".join(parsed_input.narrative_blocks)
        tags = self._extract_unique_tags(full_narrative)
        
        if not tags:
            return ""
            
        logger.info(f"Tags detetadas no input do jogador: {tags}")
        
        injected_contexts = []
        
        for tag in tags:
            logger.debug(f"A procurar metadados para: @{tag}")
            
            # PRIORIDADE 1: Atlas Local (Characters)
            context = self.asset_bridge.get_entity_metadata(tag, category="Characters")
            
            # PRIORIDADE 2: Atlas Local (Scenery)
            if not context:
                context = self.asset_bridge.get_entity_metadata(tag, category="Scenery")
                
            # PRIORIDADE 3: RAG / Memória de Longo Prazo (Se não existe fisicamente no jogo)
            if not context:
                logger.debug(f"A entidade '@{tag}' não está no Atlas. A pesquisar no ChromaDB...")
                # Foca a pesquisa em características para recuperar memórias úteis
                query = f"Quem é ou o que é {tag.replace('_', ' ')}?"
                memories = self.rag_adapter.recall_memories(query, n_results=3)
                
                if memories:
                    # Formata as memórias como uma lista de factos
                    memory_bullet_points = "\n".join(f"- {m}" for m in memories)
                    context = f"[MEMÓRIA RECUPERADA - {tag.upper()}]\n{memory_bullet_points}"
            
            # Adiciona ao buffer final se encontrou algo em qualquer uma das 3 fontes
            if context:
                injected_contexts.append(context)
            else:
                logger.warning(f"A tag '@{tag}' não retornou nenhum contexto. A IA terá de improvisar.")

        # Se encontrou informações, encapsulamos com a instrução rígida do Domínio
        if injected_contexts:
            final_block = SystemPrompts.TAG_INJECTION_HEADER.value + "\n\n".join(injected_contexts)
            return final_block
            
        return ""