from typing import Tuple
from src.domain.save_state import SaveState
from src.infrastructure.logger import get_logger

logger = get_logger("REGEN_MANAGER")

class RegenManagerUseCase:
    """
    Orquestra o Épico 17: Regeneração Unitária de Texto e Imagens.
    """
    
    def execute_regen(self, command: str, current_state: SaveState) -> Tuple[str, SaveState, str]:
        """
        Interpreta o comando de regen.
        Retorna: (Mensagem, Estado_Modificado, Tipo_De_Regeneração)
        """
        parts = command.strip().split()
        
        if len(parts) < 2 or parts[0] != "/regen":
            return "[SISTEMA] Formato inválido. Use /regen -t (texto) ou /regen -i (imagem).", current_state, "NONE"
            
        flag = parts[1].lower()
        
        if not current_state or not current_state.context_buffer:
            return "[SISTEMA] Não há contexto suficiente na campanha atual para regerar.", current_state, "NONE"

        # FLUXO 1: Regerar Texto (Apaga a última resposta da IA)
        if flag in ["-text", "-t"]:
            last_entry = current_state.context_buffer[-1]
            
            # Verificação de segurança: Só apagamos se NÃO for uma ação/fala do jogador.
            # O InputProcessor do Épico 8 formata os inputs do jogador com prefixos como [AÇÃO] ou [FALA].
            if not last_entry.startswith("[AÇÃO]") and not last_entry.startswith("[FALA]"):
                current_state.context_buffer.pop()
                logger.info("Última resposta da IA descartada. Sinalizando regeneração de texto.")
                return "[SISTEMA] Última narrativa descartada. Gerando nova resposta...", current_state, "TEXT"
            else:
                logger.warning("Regen negado: A última entrada do buffer pertence ao jogador.")
                return "[SISTEMA] A última entrada foi uma ação sua. A IA ainda não respondeu, logo, não é possível regerar.", current_state, "NONE"

        # FLUXO 2: Regerar Imagem (Preserva o texto intacto)
        elif flag in ["-img", "-i"]:
            logger.info("Sinalizando regeneração visual para a cena atual.")
            return "[SISTEMA] Solicitando nova imagem ao ComfyUI para a cena atual...", current_state, "IMAGE"

        # FALLBACK: Flag inválida
        else:
            return f"[SISTEMA] Flag desconhecida ('{flag}'). Use -t ou -i.", current_state, "NONE"