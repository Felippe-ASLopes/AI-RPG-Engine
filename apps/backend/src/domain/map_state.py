from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class MapNode(BaseModel):
    """Representa um local descoberto no mapa (Épico 30)."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str
    biome: str
    description: str = ""
    # Coordenadas relativas para o Frontend renderizar no Canvas
    x: float = 0.0
    y: float = 0.0
    # Caminhos para os assets gerados pelo ComfyUI
    tile_image_path: Optional[str] = None
    icon_image_path: Optional[str] = None

class MapConnection(BaseModel):
    """Representa a trilha narrativa/caminho percorrido entre dois locais."""
    from_node_id: str
    to_node_id: str

class MapState(BaseModel):
    """Estado topológico completo da campanha."""
    nodes: List[MapNode] = Field(default_factory=list)
    connections: List[MapConnection] = Field(default_factory=list)
    current_location_id: Optional[str] = None