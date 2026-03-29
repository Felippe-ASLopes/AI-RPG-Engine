import re
from src.infrastructure.logger import get_logger

logger = get_logger("SETUP_ASSETS")

class SetupAssetManagerUseCase:
    """
    Gerencia a vinculação de imagens às entidades durante a criação da campanha (Épico 15).
    """
    
    def __init__(self, asset_bridge):
        self.asset_bridge = asset_bridge
        self.allowed_categories = ["Characters", "Scenery"]

    def _sanitize_filename(self, name: str) -> str:
        """
        Remove espaços e caracteres especiais para criar nomes de arquivos seguros.
        Ex: 'Rei Arthur (O Louco)!' -> 'rei_arthur_o_louco'
        """
        # Converte para minúsculas e troca espaços por underscores
        safe_name = name.lower().strip().replace(" ", "_")
        # Remove tudo que não for alfanumérico ou underscore
        safe_name = re.sub(r'[^a-z0-9_]', '', safe_name)
        return safe_name

    def save_asset(self, entity_name: str, category: str, image_bytes: bytes, extension: str) -> str:
        """
        Recebe o upload, higieniza os dados e envia para persistência.
        Retorna o caminho da imagem para ser inserido no objeto CampaignSetup.
        """
        if category not in self.allowed_categories:
            logger.error(f"Tentativa de salvar asset em categoria proibida: {category}")
            raise ValueError(f"Categoria inválida. Use apenas: {self.allowed_categories}")
            
        if extension.lower() not in [".png", ".jpg", ".jpeg", ".webp"]:
            logger.warning(f"Formato de imagem não recomendado: {extension}")
            
        safe_name = self._sanitize_filename(entity_name)
        
        logger.info(f"Processando vinculação de imagem para a entidade '{entity_name}' (Nome seguro: {safe_name})")
        
        # O adaptador salva e devolve o caminho relativo
        final_path = self.asset_bridge.save_entity_image(safe_name, category, image_bytes, extension)
        
        return final_path