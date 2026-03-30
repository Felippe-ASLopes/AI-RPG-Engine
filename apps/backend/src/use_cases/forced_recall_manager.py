from src.domain.player_input import ParsedInput
from src.domain.prompts import SystemPrompts
from src.infrastructure.logger import get_logger

logger = get_logger("FORCED_RECALL")

class ForcedRecallUseCase:
    """
    Implementa o Épico 10: Acesso Manual ao RAG (The Forced Recall).
    Processa o bloco '?' e injeta lembranças específicas no contexto.
    """
    def __init__(self, rag_adapter):
        self.rag_adapter = rag_adapter

    def process_forced_queries(self, parsed_input: ParsedInput) -> str:
        if not parsed_input.forced_queries:
            return ""
            
        logger.info(f"A processar {len(parsed_input.forced_queries)} consultas forçadas de memória...")
        
        injected_contexts = []
        
        for query in parsed_input.forced_queries:
            logger.debug(f"Pesquisa exata disparada: '{query}'")
            
            memories = self.rag_adapter.recall_exact_match(query, n_results=2)
            
            if memories:
                memory_bullet_points = "\n".join(f"- {m}" for m in memories)
                injected_contexts.append(f"[PESQUISA: '{query.upper()}']\n{memory_bullet_points}")
            else:
                injected_contexts.append(f"[PESQUISA: '{query.upper()}']\n- Nenhum registo exato encontrado no diário da campanha para este termo.")

        # Junta tudo sob o cabeçalho rígido de prioridade
        final_block = SystemPrompts.FORCED_RECALL_HEADER.value + "\n\n".join(injected_contexts)
        return final_block