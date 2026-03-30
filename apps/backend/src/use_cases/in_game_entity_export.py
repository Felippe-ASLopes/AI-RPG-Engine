import json
import re
from src.domain.campaign_setup import EntityAttributes
from src.domain.prompts import SystemPrompts, UserPrompts
from src.domain.llm import LLMGenerationRequest, ChatMessage
from src.infrastructure.logger import get_logger

logger = get_logger("ENTITY_EXPORT")

class InGameEntityExportUseCase:
    """
    Implementa o Épico 36: Extração de Presets em tempo real (/save -e @tag).
    Transforma entidades orgânicas geradas na narrativa em arquivos reutilizáveis.
    """
    def __init__(self, rag_adapter, llm_adapter, preset_repository):
        self.rag_adapter = rag_adapter
        self.llm_adapter = llm_adapter
        self.preset_repository = preset_repository

    def _sanitize_name(self, name: str) -> str:
        safe = name.lower().replace("@", "").strip().replace(" ", "_")
        return re.sub(r'[^a-z0-9_]', '', safe)

    async def execute_extraction(self, command: str) -> str:
        parts = command.strip().split()
        
        # Validação do formato do comando
        if len(parts) != 3 or parts[0] != "/save" or parts[1] not in ["-entity", "-e"]:
            return "[SISTEMA] Formato inválido. Use: /save -e @nome_da_entidade"
        
        raw_entity_name = parts[2]
        safe_name = self._sanitize_name(raw_entity_name)
        display_name = raw_entity_name.replace("@", "").replace("_", " ").title()

        logger.info(f"Iniciando extração in-game para a entidade: '{display_name}'")

        # 1. Recupera as memórias da entidade do RAG
        # Pesquisamos usando o nome para pescar fragmentos relevantes de campanhas passadas
        query = f"Detalhes, ações e aparência sobre {display_name}"
        memories = self.rag_adapter.recall_memories(query, n_results=5)
        
        if not memories:
            logger.warning(f"RAG vazio para {display_name}. A IA criará do zero.")
            memory_context = "Nenhuma memória prévia encontrada. Crie a entidade do zero baseando-se no nome."
        else:
            memory_context = "\n".join(f"- {m}" for m in memories)

        # 2. Constrói o Prompt para a LLM
        system_instruction = SystemPrompts.WIZARD_ASSISTANT.value
        user_prompt = UserPrompts.EXTRACT_ENTITY_PRESET.value.format(
            entity_name=display_name,
            memory_context=memory_context
        )

        request = LLMGenerationRequest(
            messages=[
                ChatMessage(role="system", content=system_instruction),
                ChatMessage(role="user", content=user_prompt)
            ],
            temperature=0.7,
            max_tokens=800
        )

        # 3. Chama a LLM para formatar o JSON
        logger.debug(f"Processando JSON da entidade {display_name} via IA...")
        response = await self.llm_adapter.generate_text(request)

        try:
            raw_content = response.content.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:-3].strip()
                
            data = json.loads(raw_content)
            
            # Valida com o Domínio para garantir que a IA respeitou a estrutura
            entity_setup = EntityAttributes(**data)
            
            # 4. Salva no Repositório Global
            success = self.preset_repository.save_entity_preset(safe_name, entity_setup.model_dump())
            
            if success:
                logger.info(f"Entidade '{display_name}' exportada com sucesso para a Global Library!")
                return f"[SISTEMA] A entidade '{display_name}' foi catalogada e salva com sucesso na sua Biblioteca Global!"
            else:
                return f"[SISTEMA] Erro ao salvar o arquivo físico da entidade '{display_name}'."
                
        except json.JSONDecodeError:
            logger.error("Falha ao fazer parse do JSON gerado pela IA na extração.")
            return "[SISTEMA] Falha na extração. A IA não conseguiu formatar os dados corretamente."
        except Exception as e:
            logger.error(f"Erro de validação durante a extração: {str(e)}")
            return f"[SISTEMA] Ocorreu um erro ao estruturar os atributos de '{display_name}'."