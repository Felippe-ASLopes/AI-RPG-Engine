import json
from pathlib import Path
from src.domain.save_state import SaveState
from src.infrastructure.logger import get_logger

logger = get_logger("SAVE_REPO")

class JsonSaveRepository:
    """
    Adaptador para serializar o contexto em arquivos JSON locais.
    """
    def __init__(self, base_data_path: str = "../../../../data/sqlite"):
        current_dir = Path(__file__).parent
        self.save_path = (current_dir / base_data_path).resolve()
        
        logger.info(f"Repositório de Saves inicializado em: {self.save_path}")
        self._ensure_directory()

    def _ensure_directory(self):
        self.save_path.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, state: SaveState, overwrite: bool = False) -> bool:
        filepath = self.save_path / f"{filename}.json"
        
        if filepath.exists() and not overwrite:
            logger.warning(f"Tentativa de sobrescrever save negada: {filename}. Use --overwrite.")
            return False
            
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state.model_dump(), f, indent=4, ensure_ascii=False)
            logger.info(f"Campanha '{state.campaign_name}' salva em disco: {filename}.json")
            return True
        except Exception as e:
            logger.error(f"Erro ao escrever arquivo de save: {str(e)}")
            return False
        
    def load(self, filename: str) -> SaveState | None:
        """
        Lê um ficheiro JSON local e reconstrói a entidade SaveState.
        """
        filepath = self.save_path / f"{filename}.json"
        
        if not filepath.exists():
            logger.error(f"Ficheiro de save não encontrado no disco: {filename}.json")
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Dados da campanha '{data.get('campaign_name')}' extraídos com sucesso.")
            return SaveState(**data)
            
        except Exception as e:
            logger.error(f"Erro ao analisar o ficheiro de save {filename}: {str(e)}")
            return None