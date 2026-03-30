from src.domain.save_state import SaveState
from src.domain.prompts import SystemPrompts
from src.domain.llm import LLMGenerationRequest, ChatMessage
from src.infrastructure.logger import get_logger

logger = get_logger("WEB_SEARCH_MGR")

class WebSearchManagerUseCase:
    """
    Orquestra o Épico 6: Pesquisa na Web e Sanity Check.
    """
    def __init__(self, search_adapter, llm_adapter):
        self.search_adapter = search_adapter
        self.llm_adapter = llm_adapter

    async def execute_command(self, command: str, current_state: SaveState) -> str:
        if not current_state:
            return "[SISTEMA] Nenhuma campanha ativa para contextualizar a pesquisa."

        parts = command.strip().split()
        if len(parts) < 2 or parts[0] != "/search":
            return "[SISTEMA] Formato inválido. Use /search [sua consulta]."

        query = " ".join(parts[1:])
        
        logger.info(f"Avaliando viabilidade da pesquisa web: '{query}'")

        # 1. TAREFA 6.2: Filtro de "Sanity Check"
        # Fornecemos à LLM o contexto dos últimos turnos para que ela julgue a imersão
        recent_context = " ".join(current_state.context_buffer[-3:]) if current_state.context_buffer else "Início da aventura."
        
        sanity_prompt = SystemPrompts.SANITY_CHECK.value.format(
            query=query,
            campaign_name=current_state.campaign_name,
            context=recent_context
        )
        
        request = LLMGenerationRequest(
            messages=[ChatMessage(role="user", content=sanity_prompt)],
            temperature=0.0, # Temperatura 0 para garantir que responde só SIM ou NAO de forma determinística
            max_tokens=10
        )
        
        try:
            sanity_response = await self.llm_adapter.generate_text(request)
            decision = sanity_response.content.strip().upper()
            
            # Remove pontuações caso a LLM responda "SIM." ou "NÃO"
            if "NAO" in decision or "NÃO" in decision:
                logger.warning(f"Sanity Check BLOQUEOU a pesquisa '{query}'. Motivo: Anacronismo/Quebra de Imersão.")
                return f"[SISTEMA] O Juiz de Imersão bloqueou a pesquisa por '{query}' pois ela não faz sentido ou quebra a imersão no universo de '{current_state.campaign_name}'."
                
        except Exception as e:
            logger.error(f"Falha no Sanity Check: {e}")
            return "[SISTEMA] Ocorreu um erro ao verificar a validade da pesquisa."

        # 2. TAREFA 6.1: Executar Pesquisa na Web (Aprovada)
        logger.info(f"Sanity Check aprovado. Pesquisando '{query}' na internet...")
        try:
            results = await self.search_adapter.search(query, max_results=3)
            
            if not results:
                return f"[SISTEMA] A pesquisa web por '{query}' não retornou resultados."
                
            formatted_results = f"\n[WEB] Resultados encontrados para '{query}':\n"
            for r in results:
                formatted_results += f"- {r.snippet} (Fonte: {r.url})\n"
                
            logger.info("Pesquisa web concluída com sucesso.")
            return formatted_results.strip()
            
        except Exception as e:
            logger.error(f"Falha na comunicação com o motor de busca: {e}")
            return "[SISTEMA] A internet do mundo real está inacessível no momento."