import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.oracle_manager import OracleManagerUseCase
from src.domain.llm import LLMGenerationResponse

@pytest.mark.asyncio
async def test_execute_oracle_query_success():
    """Garante que o Oracle Mode consulta o RAG e formata a resposta sem gerar imagens."""
    mock_rag = MagicMock()
    mock_rag.recall_memories.return_value = ["Goblins odeiam fogo e luz brilhante."]
    
    mock_llm = AsyncMock()
    mock_llm.generate_text.return_value = LLMGenerationResponse(
        content="Goblins são fracos contra fogo.", 
        tokens_used=50
    )
    
    use_case = OracleManagerUseCase(rag_adapter=mock_rag, llm_adapter=mock_llm)
    
    response_text = await use_case.execute_query("Qual a fraqueza dos goblins?")
    
    # Validações
    mock_rag.recall_memories.assert_called_once_with("Qual a fraqueza dos goblins?", n_results=3)
    mock_llm.generate_text.assert_awaited_once()
    assert "Goblins são fracos contra fogo." in response_text

@pytest.mark.asyncio
async def test_execute_oracle_query_empty():
    use_case = OracleManagerUseCase(MagicMock(), AsyncMock())
    response_text = await use_case.execute_query("   ")
    assert "formato inválido" in response_text.lower()