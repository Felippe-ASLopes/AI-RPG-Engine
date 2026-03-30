import os
from dotenv import load_dotenv
from src.infrastructure.logger import get_logger

logger = get_logger("CONFIG")

# Carrega as variáveis do ficheiro .env para a memória
load_dotenv()

class AppConfig:
    """
    Centraliza o acesso às variáveis de ambiente (Épico 33).
    Usa valores de fallback (default) caso o utilizador esqueça de criar o .env.
    """
    MAX_INPUT_CHARACTERS: int = int(os.getenv("MAX_INPUT_CHARACTERS", "2000"))
    TOTAL_VRAM_GB: float = float(os.getenv("TOTAL_VRAM_GB", "8.0"))

logger.info(f"Configurações de Hardware carregadas: VRAM={AppConfig.TOTAL_VRAM_GB}GB, InputMax={AppConfig.MAX_INPUT_CHARACTERS}chars")