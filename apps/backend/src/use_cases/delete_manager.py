import re
from src.domain.save_state import SaveState
from src.infrastructure.logger import get_logger

logger = get_logger("DELETE_MANAGER")

class DeleteManagerUseCase:
    """
    Orquestra o Épico 38: Exclusão segura de Saves (com limpeza de RAG) e Presets globais.
    """
    def __init__(self, save_repository, preset_repository, rag_adapter):
        self.save_repository = save_repository
        self.preset_repository = preset_repository
        self.rag_adapter = rag_adapter

    def _sanitize_name(self, name: str) -> str:
        safe = name.lower().replace("@", "").strip().replace(" ", "_")
        return re.sub(r'[^a-z0-9_]', '', safe)

    def execute_delete(self, command: str, current_state: SaveState) -> str:
        parts = command.strip().split()
        
        # Validação do formato base (/save -flag alvo)
        if len(parts) != 3 or parts[0] != "/save":
            return "[SISTEMA] Formato inválido para exclusão."
        
        flag = parts[1].lower()
        target_name = parts[2]

        # FLUXO 1: Excluir Save e Limpar RAG
        if flag in ["-delete", "-d"]:
            logger.info(f"Iniciando rotina de exclusão profunda para o save: '{target_name}'")
            
            # Precisamos carregar o save alvo para descobrir a qual campanha ele pertence
            state_to_delete = self.save_repository.load(target_name)
            
            if not state_to_delete:
                return f"[SISTEMA] Falha ao excluir. O save '{target_name}' não foi encontrado no disco."
                
            campaign_name = state_to_delete.campaign_name
            
            # PROTEÇÃO DE CONTEXTO ATIVO: Impede que o usuário delete o chão onde está pisando
            if current_state and current_state.campaign_name == campaign_name:
                logger.warning(f"Tentativa de exclusão bloqueada: '{target_name}' pertence à campanha ativa.")
                return f"[SISTEMA] Acesso negado. Você não pode deletar o save '{target_name}' porque ele pertence à campanha ('{campaign_name}') que está atualmente carregada na sessão."

            # 1. Limpa as memórias (ChromaDB)
            self.rag_adapter.delete_campaign_collection(campaign_name)
            
            # 2. Deleta o arquivo de texto (JSON)
            success = self.save_repository.delete(target_name)
            
            if success:
                return f"[SISTEMA] Operação concluída: O save '{target_name}' e as memórias vetoriais da campanha '{campaign_name}' foram expurgados permanentemente."
            else:
                return f"[SISTEMA] Erro ao tentar remover o arquivo físico do save '{target_name}'."

        # FLUXO 2: Excluir Preset
        elif flag in ["-deletepreset", "-dp"]:
            safe_name = self._sanitize_name(target_name)
            logger.info(f"Iniciando exclusão de preset na Biblioteca Global: '{safe_name}'")
            
            success = self.preset_repository.delete_entity_preset(safe_name)
            
            if success:
                return f"[SISTEMA] O preset '{target_name}' foi excluído permanentemente da sua Biblioteca Global."
            else:
                return f"[SISTEMA] Falha ao excluir. O preset '{target_name}' não foi encontrado."

        else:
            return f"[SISTEMA] Flag de exclusão desconhecida ('{flag}')."