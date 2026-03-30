import json
from src.domain.campaign_setup import CampaignSetup
from src.domain.llm import LLMGenerationRequest, ChatMessage
from src.domain.prompts import SystemPrompts, UserPrompts
from src.infrastructure.logger import get_logger
from src.infrastructure.config import AppConfig

logger = get_logger("CAMPAIGN_WIZARD")

class CampaignWizardUseCase:
    """
    Orquestra a criação inicial da campanha (Épico 14), gerando as entidades primárias
    e o roteiro de forma dinâmica.
    """
    
    def __init__(self, llm_adapter):
        self.llm_adapter = llm_adapter

    async def generate_campaign(self, partial_data: dict) -> CampaignSetup:
        """
        Avalia os dados enviados pela interface. Se o jogador preencheu tudo,
        apenas valida. Se faltarem dados, pede para a LLM completar.
        """
        logger.info("Analisando dados de setup da campanha...")

        # INJEÇÃO DAS VARIÁVEIS DE AMBIENTE (.ENV) ANTES DA VALIDAÇÃO DO DOMÍNIO
        # Se o jogador não enviou preferências de restrição de conteúdo pela interface, 
        # aplicamos os valores padrão definidos no arquivo .env
        if "content_gating" not in partial_data:
            logger.debug("Preferências de conteúdo não fornecidas. Aplicando padrões do .env.")
            partial_data["content_gating"] = {
                "allow_nsfw": AppConfig.DEFAULT_ALLOW_NSFW,
                "allow_gore": AppConfig.DEFAULT_ALLOW_GORE,
                "banned_topics": []
            }
        
        try:
            # Tenta instanciar a entidade final. Se não faltar nenhum campo 
            # obrigatório, o Pydantic vai aprovar direto.
            setup = CampaignSetup(**partial_data)
            logger.info("Todos os campos obrigatórios foram fornecidos pelo jogador. Ignorando a geração por IA.")
            return setup
            
        except ValueError:
            # O Pydantic rejeitou, o que significa que o usuário deixou campos em branco.
            logger.info("Dados parciais detectados. Acionando a LLM para autocompletar o mundo...")

        # Converte o dicionário parcial numa string bonita para a IA ler
        partial_json_str = json.dumps(partial_data, ensure_ascii=False, indent=2)

        system_instruction = SystemPrompts.WIZARD_ASSISTANT.value
        user_prompt = UserPrompts.WIZARD_DYNAMIC_TEMPLATE.value.format(partial_data=partial_json_str)
        
        request = LLMGenerationRequest(
            messages=[
                ChatMessage(role="system", content=system_instruction),
                ChatMessage(role="user", content=user_prompt)
            ],
            temperature=0.8,
            max_tokens=1000 # Margem segura para a geração do JSON
        )
        
        response = await self.llm_adapter.generate_text(request)
        
        try:
            raw_content = response.content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:-3].strip()
                
            data = json.loads(raw_content)
            
            # Validação Final: Garantir que a IA preencheu o que faltava sem quebrar a estrutura
            final_setup = CampaignSetup(**data)
            
            logger.info(f"Campanha dinâmica completada pela IA com sucesso: '{final_setup.campaign_name}'. Tokens gastos: {response.tokens_used}")
            return final_setup
            
        except json.JSONDecodeError as e:
            logger.error("A IA falhou em retornar um formato JSON puro.")
            raise ValueError("Falha na formatação. A saída da IA não pôde ser interpretada como JSON.") from e
        except Exception as e:
            logger.error(f"Erro de validação após retorno da IA: {str(e)}")
            raise ValueError("A IA falhou em gerar todos os campos obrigatórios da campanha.") from e