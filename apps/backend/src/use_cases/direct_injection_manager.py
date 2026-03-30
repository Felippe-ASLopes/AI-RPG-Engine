from src.infrastructure.logger import get_logger

logger = get_logger("DIRECT_INJECTION")

class DirectInjectionUseCase:
    """
    Épico 16: Injeção Direta de Contexto (The Override).
    Processa o comando /insert e guarda factos absolutos no RAG.
    """
    def __init__(self, rag_adapter):
        self.rag_adapter = rag_adapter

    def execute_injection(self, command: str) -> str:
        parts = command.strip().split(maxsplit=1)
        
        # Valida se o comando tem o formato correto e se há texto após o /insert
        if len(parts) < 2 or parts[0] != "/insert" or not parts[1].strip():
            logger.warning("Tentativa de injeção vazia ou mal formatada.")
            return "[SISTEMA] Formato inválido. Use: /insert [facto que deseja gravar no mundo]"
        
        fact_text = parts[1].strip()
        logger.info("Processando injeção direta de contexto no RAG...")
        
        success = self.rag_adapter.save_memory(fact_text)
        
        if success:
            return f"[SISTEMA] Facto injetado com sucesso na memória do mundo: '{fact_text}'"
        else:
            return "[SISTEMA] Ocorreu um erro ao tentar gravar a memória no banco vetorial."