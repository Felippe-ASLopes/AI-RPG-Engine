from src.domain.image_generation import ImageGenerationRequest, ImageGenerationResponse
from src.domain.save_state import SaveState
from src.infrastructure.logger import get_logger

logger = get_logger("IMAGE_GEN")

class ImageGeneratorUseCase:
    """
    Orquestra o Épico 5: Mapeamento de @tags para LoRAs e envio para o ComfyUI.
    """
    def __init__(self, comfyui_adapter, preset_repository=None):
        self.comfyui_adapter = comfyui_adapter
        self.preset_repository = preset_repository # Para procurar se a @tag tem um modelo LoRA

    async def generate_scene_image(self, scene_description: str, current_state: SaveState) -> ImageGenerationResponse:
        if not scene_description:
            return ImageGenerationResponse(success=False, error_message="Descrição vazia.")

        # 1. Identificação de LoRAs (Tarefa 5.3)
        active_loras = []
        if self.preset_repository and current_state.active_tags:
            for tag in current_state.active_tags:
                lora_file = self.preset_repository.get_lora_for_entity(tag)
                if lora_file:
                    active_loras.append(lora_file)
                    logger.debug(f"LoRA '{lora_file}' ativada para a tag @{tag}.")

        # 2. Continuidade Visual (Tarefa 5.2 - IP Adapter)
        # Verifica se existe uma imagem anterior no estado para servir de base de estilo
        ref_image = getattr(current_state, "last_image_path", None)

        # 3. Construção do Pedido
        request = ImageGenerationRequest(
            prompt=f"masterpiece, best quality, rpg fantasy art, {scene_description}",
            loras=active_loras,
            reference_image_path=ref_image
        )

        # 4. Envio ao Motor
        response = await self.comfyui_adapter.generate_image(request)
        
        # 5. Atualização de Estado
        if response.success and response.image_path:
            current_state.last_image_path = response.image_path
            logger.info(f"Cena gerada e salva no estado: {response.image_path}")
            
        return response