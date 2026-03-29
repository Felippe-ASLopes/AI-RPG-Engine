import re
from src.domain.campaign_setup import CampaignSetup, EntityAttributes
from src.infrastructure.logger import get_logger

logger = get_logger("PRESET_MANAGER")

class PresetManagerUseCase:
    """
    Orquestra o Épico 23: Sistema de Presets Modulares e o auto-save de templates de campanhas.
    """
    def __init__(self, preset_repository):
        self.preset_repository = preset_repository

    def _sanitize_filename(self, name: str) -> str:
        safe_name = name.lower().strip().replace(" ", "_")
        safe_name = re.sub(r'[^a-z0-9_]', '', safe_name)
        return safe_name

    def auto_save_template(self, setup: CampaignSetup):
        """
        Requisito 23.3: Gera automaticamente o ficheiro .template que congela o estado inicial.
        Deve ser chamado imediatamente após o CampaignWizard gerar o setup com sucesso.
        """
        safe_name = self._sanitize_filename(setup.campaign_name)
        logger.info(f"Iniciando Auto-Save do Template da Campanha: '{setup.campaign_name}'")
        
        success = self.preset_repository.save_template(safe_name, setup)
        if not success:
            raise IOError("Falha ao gerar o ficheiro .template da campanha.")

    def export_nested_presets(self, setup: CampaignSetup):
        """
        Requisito 23.1: Hierarquia de Presets. Varre a campanha e exporta os Companheiros 
        e Rivais para a Biblioteca Global como presets individuais.
        """
        logger.info(f"A extrair presets modulares da campanha: '{setup.campaign_name}'")
        
        exported_count = 0
        
        # Extrai companheiros
        for companion in setup.companions:
            safe_name = self._sanitize_filename(companion.name)
            if self.preset_repository.save_entity_preset(safe_name, companion.model_dump()):
                exported_count += 1
                
        # Extrai rivais
        for rival in setup.rivals:
            safe_name = self._sanitize_filename(rival.name)
            if self.preset_repository.save_entity_preset(safe_name, rival.model_dump()):
                exported_count += 1
                
        logger.info(f"Extração concluída. {exported_count} NPCs exportados para a Global Library.")

    def import_entity_preset(self, entity_name: str) -> EntityAttributes:
        """
        Requisito 23.2: Cross-Campaign Loading. Permite carregar um NPC previamente guardado
        para ser injetado num novo formulário de campanha.
        """
        safe_name = self._sanitize_filename(entity_name)
        logger.info(f"A tentar importar preset de entidade: '{entity_name}'")
        
        data = self.preset_repository.load_entity_preset(safe_name)
        
        if not data:
            raise ValueError(f"O preset para '{entity_name}' não existe na biblioteca global.")
            
        try:
            # Valida através do Domínio para garantir que o JSON externo não foi corrompido
            entity = EntityAttributes(**data)
            logger.info(f"Preset '{entity.name}' importado e validado com sucesso.")
            return entity
        except Exception as e:
            logger.error(f"Erro de validação no preset '{entity_name}': {str(e)}")
            raise ValueError("O ficheiro de preset está corrompido ou é inválido.") from e