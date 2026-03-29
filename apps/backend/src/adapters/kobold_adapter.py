import httpx
from typing import List
from src.domain.llm import LLMGenerationRequest, LLMGenerationResponse, ChatMessage
from src.domain.prompts import RPG_SYSTEM_PROMPT

class KoboldCPPAdapter:
    def __init__(self, base_url: str = "http://localhost:5001/v1"):
        self.base_url = base_url

    # Gera uma resposta assíncrona comunicando-se com a API do KoboldCPP.
    async def generate_text(self, request: LLMGenerationRequest, additional_system_context: str = "") -> LLMGenerationResponse:
        # Constrói o System Prompt final injetando contexto adicional (metadados/RAG)
        final_system_prompt = RPG_SYSTEM_PROMPT
        if additional_system_context:
            final_system_prompt += f"\n\nCONTEXTO ADICIONAL DA CENA:\n{additional_system_context}"

        # Prepara a lista de mensagens garantindo que o System venha primeiro
        payload_messages = [{"role": "system", "content": final_system_prompt}]
        for msg in request.messages:
            payload_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "messages": payload_messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "mode": "chat"
        }

        # Chamada assíncrona ao LLM local
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            generated_text = data['choices'][0]['message']['content']
            tokens_used = data['usage']['total_tokens']

            return LLMGenerationResponse(
                content=generated_text,
                tokens_used=tokens_used
            )