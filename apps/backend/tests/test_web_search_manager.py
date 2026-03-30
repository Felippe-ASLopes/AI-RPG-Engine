import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.web_search_manager import WebSearchManagerUseCase
from src.domain.save_state import SaveState
from src.domain.web_search import SearchResult
from src.domain.llm import LLMGenerationResponse

@pytest.fixture
def mock_search_adapter():
    adapter = MagicMock()
    adapter.search = AsyncMock(return_value=[
        SearchResult(title="História de Roma", snippet="Roma foi fundada em 753 a.C.", url="http://roma.com")
    ])
    return adapter

@pytest.mark.asyncio
async def test_web_search_allowed_by_sanity_check(mock_search_adapter):
    """Testa uma pesquisa que faz sentido para o contexto (Aprovada pelo Juiz)."""
    mock_llm = MagicMock()
    mock_llm.generate_text = AsyncMock(return_value=LLMGenerationResponse(content="SIM", tokens_used=10))
    
    use_case = WebSearchManagerUseCase(search_adapter=mock_search_adapter, llm_adapter=mock_llm)
    state = SaveState(campaign_name="Império Romano", context_buffer=["Caminhando pelo fórum."], active_tags=[])
    
    msg = await use_case.execute_command("/search fundação de Roma", state)
    
    # A pesquisa deve ser executada
    mock_search_adapter.search.assert_awaited_once_with("fundação de Roma", max_results=3)
    assert "Roma foi fundada" in msg
    assert "[WEB]" in msg

@pytest.mark.asyncio
async def test_web_search_blocked_by_sanity_check(mock_search_adapter):
    """Testa a Tarefa 6.2: O Sanity Check bloqueia anacronismos."""
    mock_llm = MagicMock()
    # O LLM responde NAO porque pesquisar por iPhone em Roma Antiga quebra a imersão
    mock_llm.generate_text = AsyncMock(return_value=LLMGenerationResponse(content="NAO", tokens_used=10))
    
    use_case = WebSearchManagerUseCase(search_adapter=mock_search_adapter, llm_adapter=mock_llm)
    state = SaveState(campaign_name="Império Romano", context_buffer=["Caminhando pelo fórum."], active_tags=[])
    
    msg = await use_case.execute_command("/search comprar iphone 15", state)
    
    # A pesquisa na internet NÃO deve ser chamada!
    mock_search_adapter.search.assert_not_called()
    assert "quebra a imersão" in msg.lower()