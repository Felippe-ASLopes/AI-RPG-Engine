from typing import Tuple, Optional
from src.domain.save_state import SaveState
from src.adapters.save_repository import JsonSaveRepository
from src.adapters.vector_memory import VectorMemoryAdapter
from src.use_cases.vram_optimizer import VRAMOptimizer
from src.infrastructure.logger import logger as global_logger, get_logger

logger = get_logger("LOAD_MANAGER")

class LoadManager:
    """
    Orquestra o Épico 13 e 35: Carregamento de Snapshots e limpeza de VRAM/RAG.
    """
    def __init__(self, 
        repository: JsonSaveRepository, 
        vram_optimizer: VRAMOptimizer, 
        rag_adapter: VectorMemoryAdapter):
        self.repository = repository
        self.vram_optimizer = vram_optimizer
        self.rag_adapter = rag_adapter

    async def execute_load(self, command: str) -> Tuple[str, Optional[SaveState]]:
        parts = command.strip().split()
        
        if len(parts) != 2 or parts[0] != "/load":
            logger.debug("Comando de load mal formatado.")
            return "Erro: Formato inválido. Use /load [nome].", None
        
        filename = parts[1]
        
        # 1. Recupera o estado do repositório
        state = self.repository.load(filename)
        
        if not state:
            return f"[SISTEMA] Falha ao carregar. O save '{filename}' não foi encontrado.", None
        
        # 2. Requisito 19.1: Limpeza do Log
        global_logger._initialize() 
        logger.info(f"Nova sessão iniciada a partir do arquivo: {filename}.json")
        
        # 3. Épico 35: Limpeza Profunda de Contexto (Prevenção de Alucinação)
        logger.warning("Iniciando expurgo de contexto anterior para evitar vazamento narrativo...")
        
        await self.vram_optimizer.force_clear_vram()
        self.rag_adapter.switch_campaign_collection(state.campaign_name)
            
        logger.info("INTEGRIDADE: VRAM purgada e RAG sincronizado. Ambiente limpo.")
        
        return f"[SISTEMA] Progresso '{filename}' carregado com sucesso. Bem-vindo de volta à campanha: {state.campaign_name}.", state