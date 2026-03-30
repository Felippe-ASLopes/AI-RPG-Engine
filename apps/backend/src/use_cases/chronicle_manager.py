from src.domain.save_state import SaveState
from src.domain.prompts import SystemPrompts
from src.domain.llm import LLMGenerationRequest, ChatMessage
from src.infrastructure.logger import get_logger

logger = get_logger("CHRONICLE_MANAGER")

class ChronicleManagerUseCase:
    """Orquestra o Épico 29: Diário de Marcos Narrativos."""
    
    def __init__(self, chronicle_repository, llm_adapter):
        self.chronicle_repository = chronicle_repository
        self.llm_adapter = llm_adapter

    async def execute_command(self, command: str, current_state: SaveState) -> str:
        if not current_state:
            return "[SISTEMA] Nenhuma campanha ativa."

        parts = command.strip().split()
        if len(parts) < 2:
            return "[SISTEMA] Formato inválido. Use /chronicle -update (-u) ou /chronicle -view (-v)."

        flag = parts[1].lower()

        # FLUXO 1: ATUALIZAR (Acionado periodicamente pelo sistema ou pelo jogador)
        if flag in ["-update", "-u"]:
            logger.info("Iniciando sumarização do Diário de Marcos...")
            
            # Pega as últimas 15 interações do buffer para ter contexto suficiente
            recent_history = "\n".join(current_state.context_buffer[-15:])
            if not recent_history.strip():
                return "[SISTEMA] Histórico insuficiente para sumarizar."

            prompt = SystemPrompts.CHRONICLE_EXTRACTION.value.format(context=recent_history)
            
            # Request com Temperatura baixa (0.3) para forçar respostas literais sem criatividade inventada
            request = LLMGenerationRequest(
                messages=[ChatMessage(role="system", content=prompt)],
                temperature=0.3, 
                max_tokens=250
            )
            
            try:
                response = await self.llm_adapter.generate_text(request)
                milestones = response.content.strip()
                
                if milestones:
                    self.chronicle_repository.append_milestones(current_state.campaign_name, milestones)
                    logger.info("Diário de Marcos atualizado com sucesso no arquivo .md.")
                    return "[SISTEMA] O Diário de Marcos foi atualizado com as últimas conquistas!"
                else:
                    logger.debug("Nenhum evento de alto impacto detectado pela IA.")
                    return "[SISTEMA] Nenhum evento de alto impacto recente para registrar."
            except Exception as e:
                logger.error(f"Falha ao consultar a IA para o Diário: {e}")
                return "[SISTEMA] Falha ao atualizar o Diário de Marcos."

        # FLUXO 2: VISUALIZAR (Para o Frontend construir a timeline)
        elif flag in ["-view", "-v"]:
            content = self.chronicle_repository.read_chronicle(current_state.campaign_name)
            return f"\n=== DIÁRIO DE MARCOS ===\n{content}\n========================"

        return f"[SISTEMA] Flag desconhecida ('{flag}')."