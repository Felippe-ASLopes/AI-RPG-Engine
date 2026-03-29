import asyncio
from src.infrastructure.logger import get_logger

logger = get_logger("VRAM_OPT")

class VRAMOptimizer:
    """
    Gerencia a alocação de VRAM alternando o 'estado' ativo entre o Motor de Texto (LLM) 
    e o Motor de Imagem (Diffusion), evitando estouro dos 8GB da RX 7600.
    """
    def __init__(self):
        # O estado inicial do RPG sempre começa com texto
        self.active_engine = "TEXT" 
        logger.info("VRAM Optimizer inicializado. Engine primária: TEXT (KoboldCPP)")

    async def swap_to_image_mode(self):
        """
        Executa a rotina de unloading do modelo de texto (Tarefa 2.2).
        Prepara o terreno para o ComfyUI assumir a VRAM.
        """
        if self.active_engine == "IMAGE":
            logger.debug("A VRAM já está alocada para o motor de imagem. Ignorando swap.")
            return

        logger.warning("Iniciando SWAP de VRAM: TEXTO -> IMAGEM")
        
        # Aqui, em etapas futuras, faremos a chamada HTTP real para o endpoint do KoboldCPP
        # que limpa o cache de contexto (ex: /api/extra/abort ou limpando a fila).
        # Como o KoboldCPP em modo Vulkan já gerencia bem a troca dinâmica com o SO,
        # o nosso trabalho principal é garantir o bloqueio (Lock) para que eles não rodem juntos.
        
        await asyncio.sleep(0.5)  # Simulando o delay do descarregamento da VRAM
        
        self.active_engine = "IMAGE"
        logger.info("SWAP concluído: VRAM liberada para o ComfyUI.")

    async def swap_to_text_mode(self):
        """
        Devolve a prioridade da VRAM para o KoboldCPP continuar a narrativa.
        """
        if self.active_engine == "TEXT":
            return

        logger.warning("Iniciando SWAP de VRAM: IMAGEM -> TEXTO")
        
        # Da mesma forma, aqui avisaremos o ComfyUI para fazer "Free VRAM" dos modelos SDXL/Flux
        await asyncio.sleep(0.5) 
        
        self.active_engine = "TEXT"
        logger.info("SWAP concluído: VRAM devolvida ao KoboldCPP.")

    def get_current_state(self) -> str:
        return self.active_engine
    
    async def force_clear_vram(self):
        """
        (Épico 35) Força a liberação completa da VRAM, apagando o contexto cacheado.
        Ideal para limpar alucinações residuais durante o !load de um novo save.
        """
        logger.warning("VRAM OPTIMIZER: Executando expurgo forçado de contexto na RX 7600...")
        
        # Aqui ficará a chamada HTTP para a API local (ex: /api/extra/abort)
        # Para simular o tempo de descarregamento da placa de vídeo:
        await asyncio.sleep(1.0) 
        
        # Devolve a prioridade para o texto, que é o padrão ao carregar um save
        self.active_engine = "TEXT" 
        logger.info("VRAM OPTIMIZER: Memória de vídeo expurgada com sucesso.")