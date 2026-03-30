import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env para a memória
load_dotenv()

class AppConfig:
    """
    Centraliza o acesso às variáveis de ambiente e gerencia caminhos dinâmicos.
    """
    # Descoberta da Raiz do Projeto (ai-rpg-engine)
    # config.py -> infrastructure -> src -> backend -> apps -> ai-rpg-engine
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[4]

    # Hardware
    TOTAL_VRAM_GB: float = float(os.getenv("TOTAL_VRAM_GB", "8.0"))
    TOTAL_RAM_GB: float = float(os.getenv("TOTAL_RAM_GB", "32.0"))
    MAX_INPUT_CHARACTERS: int = int(os.getenv("MAX_INPUT_CHARACTERS", "2000"))
    
    # APIs e Modelos
    KOBOLDCPP_PORT: int = int(os.getenv("KOBOLDCPP_PORT", "5001"))
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf")
    COMFYUI_API_URL: str = os.getenv("COMFYUI_API_URL", "http://localhost:8188")
    KOBOLD_API_URL: str = os.getenv("KOBOLD_API_URL", f"http://localhost:{KOBOLDCPP_PORT}")
    
    # Armazenamento (Junta a raiz do projeto com o caminho limpo do .env)
    CHROMA_DB_PATH: Path = PROJECT_ROOT / os.getenv("CHROMA_DB_DIR", "data/chromadb")
    SQLITE_DB_PATH: Path = PROJECT_ROOT / os.getenv("SQLITE_DB_DIR", "data/sqlite")
    ASSETS_PATH: Path = PROJECT_ROOT / os.getenv("ASSETS_DIR", "data/Assets")
    GLOBAL_LIBRARY_PATH: Path = PROJECT_ROOT / os.getenv("GLOBAL_LIBRARY_DIR", "data/Global_Library")

    # Configurações Padrão de Gating
    DEFAULT_ALLOW_NSFW: bool = os.getenv("DEFAULT_ALLOW_NSFW", "False").lower() in ("true", "1", "yes")
    DEFAULT_ALLOW_GORE: bool = os.getenv("DEFAULT_ALLOW_GORE", "False").lower() in ("true", "1", "yes")

# Evitamos importar o Logger aqui dentro para não causar import circular, 
# já que o Logger precisará ler caminhos no futuro.