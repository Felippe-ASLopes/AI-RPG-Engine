from pydantic import BaseModel, Field
from typing import List, Optional

class ImageGenerationRequest(BaseModel):
    """Encapsula os dados necessários para pedir uma imagem ao ComfyUI."""
    prompt: str
    negative_prompt: str = "text, watermark, ugly, bad anatomy, bad proportions"
    reference_image_path: Optional[str] = None # Para o IP-Adapter (Tarefa 5.2)
    loras: List[str] = Field(default_factory=list) # Para injetar personagens (Tarefa 5.3)
    width: int = 1024
    height: int = 1024

class ImageGenerationResponse(BaseModel):
    """Resposta padronizada do motor visual."""
    success: bool
    image_path: Optional[str] = None
    error_message: Optional[str] = None