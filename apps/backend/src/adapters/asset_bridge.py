import os
import json
from pathlib import Path
from src.infrastructure.logger import get_logger

logger = get_logger("ASSET_BRIDGE")

class AssetBridgeAdapter:
    """
    Escaneia os diretórios locais de Assets e extrai metadados (JSON) 
    para injeção dinâmica no prompt da LLM (Épico 3).
    """
    def __init__(self, base_data_path: str = "../../../../data/Assets"):
        # Resolve o caminho absoluto baseado na localização deste script
        current_dir = Path(__file__).parent
        self.assets_path = (current_dir / base_data_path).resolve()
        
        self.scenery_path = self.assets_path / "Scenery"
        self.characters_path = self.assets_path / "Characters"
        
        logger.info(f"Asset Bridge inicializado. Mapeando: {self.assets_path}")
        self._ensure_directories()

    def _ensure_directories(self):
        """Garante que as pastas do Atlas existam no HD."""
        self.scenery_path.mkdir(parents=True, exist_ok=True)
        self.characters_path.mkdir(parents=True, exist_ok=True)

    def get_entity_metadata(self, entity_name: str, category: str = "Characters") -> str:
        """
        Busca um arquivo .json com o nome da entidade e retorna sua descrição.
        Retorna uma string vazia se não encontrar.
        """
        target_folder = self.characters_path if category == "Characters" else self.scenery_path
        
        # Procura por um arquivo JSON com o nome exato da entidade (case-insensitive seria ideal, 
        # mas vamos focar no exact match para simplificar inicialmente)
        json_file = target_folder / f"{entity_name}.json"
        
        if not json_file.exists():
            logger.debug(f"Metadado não encontrado para a entidade: {entity_name}")
            return ""

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Formata o contexto que será injetado na LLM
            desc = data.get("description", "")
            tags = ", ".join(data.get("tags", []))
            
            contexto = f"[ATLAS LOCAL - {category.upper()}] {entity_name}\nDescrição: {desc}\nTags: {tags}"
            logger.info(f"Metadados carregados com sucesso para: @{entity_name}")
            return contexto
            
        except Exception as e:
            logger.error(f"Erro ao ler metadados de {entity_name}: {str(e)}")
            return ""