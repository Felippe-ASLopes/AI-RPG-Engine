import json
from pathlib import Path
from src.domain.player_input import ActiveCheats
from src.infrastructure.logger import get_logger
from src.infrastructure.config import AppConfig

logger = get_logger("CHEAT_REPO")

class JsonCheatRepository:
    """
    Adaptador para serializar regras impostas e trapaças ($).
    """
    def __init__(self, base_data_path: Path = AppConfig.PROJECT_ROOT / "data"):
        self.file_path = base_data_path / "active_cheats.json"
        
        logger.info(f"Repositório de Trapaças inicializado. Alvo: {self.file_path}")
        self._ensure_directory(base_data_path)

    def _ensure_directory(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)

    def load_cheats(self) -> ActiveCheats:
        if not self.file_path.exists():
            return ActiveCheats()
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ActiveCheats(**data)
        except Exception as e:
            logger.error(f"Erro ao analisar o arquivo active_cheats.json: {str(e)}")
            return ActiveCheats()
            
    def save_cheats(self, cheats: ActiveCheats) -> bool:
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(cheats.model_dump(), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Falha ao escrever arquivo active_cheats.json: {str(e)}")
            return False