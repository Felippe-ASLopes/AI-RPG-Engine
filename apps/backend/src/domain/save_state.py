from pydantic import BaseModel, Field
from typing import List, Optional
from src.domain.quest import Quest
from src.domain.player_hud import PlayerStats, InventoryItem
from src.domain.map_state import MapState

class SaveState(BaseModel):
    campaign_name: str
    context_buffer: List[str]
    active_tags: List[str]
    quest_log: List[Quest] = Field(default_factory=list)
    stats: PlayerStats = Field(default_factory=PlayerStats)
    inventory: List[InventoryItem] = Field(default_factory=list)
    atlas: MapState = Field(default_factory=MapState)
    last_image_path: Optional[str] = None