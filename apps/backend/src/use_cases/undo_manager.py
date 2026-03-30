from typing import Tuple, Optional
from src.domain.undo_snapshot import UndoSnapshot
from src.domain.save_state import SaveState
from src.adapters.undo_repository import JsonUndoRepository
from src.infrastructure.logger import get_logger

logger = get_logger("UNDO_MANAGER")

class UndoManagerUseCase:
    """
    Orquestra o Épico 11 (Sistema de Desfazer) e Épico 21 (Re-edit do Buffer).
    """
    def __init__(self, undo_repository: JsonUndoRepository, vram_optimizer):
        self.undo_repository = undo_repository
        self.vram_optimizer = vram_optimizer

    def save_turn(self, state: SaveState, user_input: str):
        """
        Deve ser chamado pelo orquestrador do loop de gameplay ANTES de enviar 
        o input para a LLM, garantindo que o estado prévio fique salvo.
        """
        snapshot = UndoSnapshot(state=state, last_user_input=user_input)
        self.undo_repository.save_snapshot(state.campaign_name, snapshot)
        logger.info(f"Estado salvo no Buffer de Undo (Campanha: {state.campaign_name}).")

    async def execute_undo(self, campaign_name: str) -> Tuple[str, Optional[SaveState], str]:
        """
        Recupera o último estado e devolve os dados para restaurar a sessão e a UI.
        Retorna: (Mensagem_Status, Estado_Restaurado, Input_Para_Reedicao)
        """
        logger.warning(f"Sinal de ROLLBACK recebido para a campanha: {campaign_name}")
        
        snapshot = self.undo_repository.pop_last_snapshot(campaign_name)
        
        if not snapshot:
            return "[SISTEMA] Não há ações anteriores no histórico recente para desfazer.", None, ""

        # Como a IA já gerou um futuro (que foi rejeitado), o contexto em cache na 
        # placa de vídeo (RX 7600) está "poluído". É imperativo acionar o flush da VRAM.
        await self.vram_optimizer.force_clear_vram()
        
        logger.info("Rollback concluído. A memória da IA foi purgada para evitar vazamento narrativo.")
        
        return "[SISTEMA] Ação desfeita. O tempo retrocedeu e seu último comando foi recuperado.", snapshot.state, snapshot.last_user_input