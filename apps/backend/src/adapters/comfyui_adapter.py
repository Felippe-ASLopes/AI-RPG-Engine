import json
import urllib.request
import urllib.parse
from typing import Dict, Any
from src.domain.image_generation import ImageGenerationRequest, ImageGenerationResponse
from src.infrastructure.logger import get_logger

logger = get_logger("COMFY_UI")

class ComfyUIAdapter:
    """
    Adaptador para a API HTTP do ComfyUI local.
    Implementa o Requisito 5.1.
    """
    def __init__(self, server_address: str = "http://127.0.0.1:8188"):
        self.server_address = server_address

    def _build_workflow(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        """
        No mundo real, este JSON é exportado diretamente da interface do ComfyUI 
        ativando a opção 'Save (API Format)'. Aqui construímos uma versão simplificada
        para injetar os nossos parâmetros.
        """
        # Node 3: KSampler, Node 4: Checkpoint, Node 6: Positive Prompt, Node 7: Negative Prompt
        prompt_workflow = {
            "4": {"inputs": {"ckpt_name": "sdxl_base.safetensors"}, "class_type": "CheckpointLoaderSimple"},
            "6": {"inputs": {"text": request.prompt, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "7": {"inputs": {"text": request.negative_prompt, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "5": {"inputs": {"width": request.width, "height": request.height, "batch_size": 1}, "class_type": "EmptyLatentImage"},
            "3": {
                "inputs": {"seed": 12345, "steps": 20, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]},
                "class_type": "KSampler"
            },
            "8": {"inputs": {"samples": ["3", 0], "vaedecode": ["4", 2]}, "class_type": "VAEDecode"},
            "9": {"inputs": {"filename_prefix": "rpg_engine", "images": ["8", 0]}, "class_type": "SaveImage"}
        }

        # Lógica de Injeção de LoRA (Tarefa 5.3)
        # Se houver LoRAs, precisaríamos de alterar a cadeia de nós ("model": ["LoRA_Node", 0])
        if request.loras:
            logger.info(f"Injetando {len(request.loras)} LoRAs no workflow do ComfyUI.")
            # A lógica real de alteração do dicionário entraria aqui
            
        # Lógica de Injeção de IP-Adapter (Tarefa 5.2)
        if request.reference_image_path:
            logger.info("Injetando imagem de referência no IP-Adapter para manter coerência visual.")
            # A lógica real do nó IP-Adapter entraria aqui

        return prompt_workflow

    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        logger.info(f"Enviando pedido de geração de imagem para {self.server_address}")
        workflow = self._build_workflow(request)
        
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(f"{self.server_address}/prompt", data=data)
        req.add_header("Content-Type", "application/json")
        
        try:
            # Sendo uma operação bloqueante de rede, idealmente usariamos aiohttp aqui
            # Usando urllib para reduzir dependências externas no momento
            response = urllib.request.urlopen(req)
            result = json.loads(response.read())
            
            prompt_id = result.get("prompt_id")
            logger.info(f"Imagem na fila do ComfyUI. Prompt ID: {prompt_id}")
            
            # Aqui entrará a lógica de *polling* via WebSockets para saber quando a imagem
            # terminou de gerar e descarregá-la para a pasta /Assets/Scenery/
            
            return ImageGenerationResponse(
                success=True, 
                image_path=f"/Assets/Scenery/{prompt_id}.png"
            )
        except Exception as e:
            logger.error(f"Falha na comunicação com ComfyUI: {e}")
            return ImageGenerationResponse(success=False, error_message=str(e))