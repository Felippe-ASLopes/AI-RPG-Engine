import json
from pathlib import Path
from src.domain.player_input import PlayerPreferences
from src.infrastructure.logger import get_logger
from src.infrastructure.config import AppConfig

logger = get_logger("PREFS_REPO")

class JsonPreferencesRepository:
    """
    Adaptador para serializar e ler as regras de tom e mecânicas 
    no arquivo global preferences.json (Épico 7).
    """
    def __init__(self, base_data_path: Path = AppConfig.PROJECT_ROOT / "data"):
        # Armazena na raiz da pasta /data para ser global a todas as campanhas
        self.file_path = base_data_path / "preferences.json"
        
        logger.info(f"Repositório de Preferências inicializado. Alvo: {self.file_path}")
        self._ensure_directory(base_data_path)

    def _ensure_directory(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

    def load_preferences(self) -> PlayerPreferences:
        """Lê o JSON do disco. Se não existir, retorna um objeto vazio."""
        if not self.file_path.exists():
            logger.debug("Arquivo preferences.json não encontrado. Iniciando estado vazio.")
            return PlayerPreferences()
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return PlayerPreferences(**data)
        except Exception as e:
            logger.error(f"Erro ao analisar o arquivo preferences.json: {str(e)}")
            return PlayerPreferences()
            
    def save_preferences(self, prefs: PlayerPreferences) -> bool:
        """Escreve a entidade PlayerPreferences fisicamente no SSD."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(prefs.model_dump(), f, indent=4, ensure_ascii=False)
            logger.debug("Preferências do jogador salvas com sucesso em disco.")
            return True
        except Exception as e:
            logger.error(f"Falha ao escrever arquivo preferences.json: {str(e)}")
            return False