from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str  # 'system', 'user', 'assistant'
    content: str

class LLMGenerationRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: float = 0.9

class LLMGenerationResponse(BaseModel):
    content: str
    tokens_used: int