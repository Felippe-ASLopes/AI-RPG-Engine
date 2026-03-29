import json
from pathlib import Path
from src.domain.campaign_setup import CampaignSetup
from src.infrastructure.logger import get_logger

logger = get_logger("PRESET_REPO")

class JsonPresetRepository:
    """
    Adaptador para serializar presets na biblioteca global e templates de campanha.
    """
    def __init__(self, base_data_path: str = "../../../../data"):
        current_dir = Path(__file__).parent
        self.data_path = (current_dir / base_data_path).resolve()
        
        # Onde guardamos os esqueletos iniciais das campanhas
        self.templates_path = self.data_path / "sqlite" / "templates"
        
        # Requisito 24.1: Biblioteca Global de Reutilização
        self.global_library_path = self.data_path / "Global_Library"
        self.npc_presets_path = self.global_library_path / "NPCs"
        
        logger.info(f"Repositório de Presets inicializado em: {self.data_path}")
        self._ensure_directories()

    def _ensure_directories(self):
        self.templates_path.mkdir(parents=True, exist_ok=True)
        self.npc_presets_path.mkdir(parents=True, exist_ok=True)

    def save_template(self, safe_name: str, setup: CampaignSetup) -> bool:
        """Guarda o estado inicial da campanha como um ficheiro .template (JSON interno)"""
        filepath = self.templates_path / f"{safe_name}.template"
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(setup.model_dump(), f, indent=4, ensure_ascii=False)
            logger.info(f"Template de campanha guardado: {safe_name}.template")
            return True
        except Exception as e:
            logger.error(f"Erro ao guardar template de campanha {safe_name}: {str(e)}")
            return False

    def save_entity_preset(self, safe_name: str, data: dict) -> bool:
        """Guarda um NPC/Entidade individualmente na Biblioteca Global"""
        filepath = self.npc_presets_path / f"{safe_name}.json"
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.debug(f"Preset de entidade exportado para a Global Library: {safe_name}.json")
            return True
        except Exception as e:
            logger.error(f"Erro ao guardar preset de entidade {safe_name}: {str(e)}")
            return False
            
    def load_entity_preset(self, safe_name: str) -> dict | None:
        """Recupera um NPC guardado na Biblioteca Global"""
        filepath = self.npc_presets_path / f"{safe_name}.json"
        if not filepath.exists():
            logger.warning(f"Preset de entidade não encontrado: {safe_name}.json")
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao ler preset de entidade {safe_name}: {str(e)}")
            return None