from pydantic import BaseModel
from typing import List, Optional

class ContentGating(BaseModel):
    """
    Épico 25: Regras de restrição de conteúdo da campanha.
    Por padrão, para segurança, NSFW e Gore vêm desativados.
    """
    allow_nsfw: bool = False
    allow_gore: bool = False
    banned_topics: List[str] = []

class EntityAttributes(BaseModel):
    name: str
    appearance: str
    personality: str
    power_skill: str
    benefits: str
    flaws: str
    image_path: Optional[str] = None  # Novo campo para o Épico 15

class Milestone(BaseModel):
    """
    Requisito Funcional 14.3: Roteiro de Pontos de Trama (Marcos).
    """
    title: str
    description: str
    is_completed: bool = False

class CampaignSetup(BaseModel):
    """
    Estrutura central gerada pelo assistente de criação.
    Define o esqueleto do mundo antes do primeiro turno iniciar.
    """
    campaign_name: str
    theme: str
    main_character: EntityAttributes
    companions: List[EntityAttributes] = []
    rivals: List[EntityAttributes] = []
    milestones: List[Milestone] = []
    content_gating: ContentGating = ContentGating()