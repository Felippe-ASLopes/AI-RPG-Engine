import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.in_game_entity_export import InGameEntityExportUseCase
from src.domain.llm import LLMGenerationResponse

@pytest.mark.asyncio
async def test_export_entity_from_campaign_success():
    """
    Testa se o fluxo extrai corretamente memórias de uma entidade, 
    pede para a LLM formatar e salva na Global Library.
    """
    mock_rag = MagicMock()
    # Simula o RAG encontrando menções à espada
    mock_rag.recall_memories.return_value = [
        "O jogador encontrou a Lâmina do Sol escondida.",
        "A Lâmina do Sol brilha com fogo divino e queima mortos-vivos."
    ]
    
    mock_llm = AsyncMock()
    # Simula a LLM estruturando a espada como uma EntityAttributes
    fake_json = json.dumps({
        "name": "Lâmina do Sol",
        "appearance": "Espada longa banhada a ouro brilhante.",
        "personality": "Aura de calor e esperança.", # Adaptado para objetos
        "power_skill": "Dano de fogo sagrado contra mortos-vivos.",
        "benefits": "Ilumina cavernas escuras.",
        "flaws": "Atrai inimigos devido ao seu brilho constante."
    })
    mock_llm.generate_text.return_value = LLMGenerationResponse(content=fake_json, tokens_used=120)
    
    mock_preset_repo = MagicMock()
    mock_preset_repo.save_entity_preset.return_value = True
    
    use_case = InGameEntityExportUseCase(mock_rag, mock_llm, mock_preset_repo)
    
    # O usuário digita o comando no chat
    command = "!save --entity @lamina_do_sol"
    result_msg = await use_case.execute_extraction(command)
    
    # Verificações
    mock_rag.recall_memories.assert_called_once()
    mock_llm.generate_text.assert_awaited_once()
    mock_preset_repo.save_entity_preset.assert_called_once()
    
    # O nome higienizado passado pro repositório deve estar correto
    saved_name = mock_preset_repo.save_entity_preset.call_args[0][0]
    assert saved_name == "lamina_do_sol"
    assert "sucesso" in result_msg.lower()

@pytest.mark.asyncio
async def test_export_entity_invalid_command():
    use_case = InGameEntityExportUseCase(MagicMock(), AsyncMock(), MagicMock())
    result_msg = await use_case.execute_extraction("!save")
    assert "formato inválido" in result_msg.lower()