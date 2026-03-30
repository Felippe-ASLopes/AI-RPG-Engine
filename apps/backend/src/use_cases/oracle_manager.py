from src.domain.prompts import SystemPrompts
from src.domain.llm import LLMGenerationRequest, ChatMessage
from src.infrastructure.logger import get_logger

logger = get_logger("ORACLE_MANAGER")

class OracleManagerUseCase:
    """
    Implementa o Épico 32: Consulta ao Mestre (Oracle Mode).
    Permite tirar dúvidas sem avançar o turno ou gastar VRAM com imagens.
    """
    def __init__(self, rag_adapter, llm_adapter):
        self.rag_adapter = rag_adapter
        self.llm_adapter = llm_adapter

    async def execute_query(self, query: str) -> str:
        """
        Recebe a pergunta do jogador, pesquisa no RAG e devolve a resposta da LLM "em off".
        """
        query = query.strip()
        if not query:
            return "[SISTEMA] Formato inválido. Use '? [sua pergunta]'."

        logger.info(f"ORACLE MODE: Processando dúvida do jogador: '{query}'")

        # 1. Recuperação de Baixo Custo (RAG)
        memories = self.rag_adapter.recall_memories(query, n_results=3)
        
        if memories:
            memory_context = "\n".join(f"- {m}" for m in memories)
        else:
            memory_context = "Nenhuma informação específica encontrada na memória recente. Deduza a resposta baseando-se no bom senso do cenário RPG."

        # 2. Construção do Prompt do Oráculo
        system_instruction = SystemPrompts.ORACLE_MODE.value.format(context=memory_context)
        
        request = LLMGenerationRequest(
            messages=[
                ChatMessage(role="system", content=system_instruction),
                ChatMessage(role="user", content=query)
            ],
            temperature=0.5, # Menor temperatura para respostas mais diretas e factuais
            max_tokens=300
        )

        # 3. Chamada à LLM
        logger.debug("Solicitando resposta do Oráculo à LLM...")
        try:
            response = await self.llm_adapter.generate_text(request)
            logger.info(f"ORACLE MODE: Resposta gerada. Tokens gastos: {response.tokens_used}")
            return f"[ORÁCULO] {response.content.strip()}"
        except Exception as e:
            logger.error(f"Falha ao consultar o Oráculo: {str(e)}")
            return "[SISTEMA] O Mestre está inacessível no momento. Tente novamente."