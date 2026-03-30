import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.chronicle_manager import ChronicleManagerUseCase
from src.domain.save_state import SaveState
from src.domain.llm import LLMGenerationResponse

@pytest.fixture
def mock_repo():
    return MagicMock()

@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    # Simula a IA devolvendo tópicos formatados
    llm.generate_text.return_value = LLMGenerationResponse(
        content="- O herói derrotou o Rei Golem.\n- A chave de cristal foi recuperada.", 
        tokens_used=150
    )
    return llm

@pytest.mark.asyncio
async def test_update_chronicle_success(mock_repo, mock_llm):
    """Testa a sumarização automática e delegação para o repositório."""
    use_case = ChronicleManagerUseCase(chronicle_repository=mock_repo, llm_adapter=mock_llm)
    state = SaveState(campaign_name="Aventura", context_buffer=["Ação 1", "Ação 2"], active_tags=[])
    
    msg = await use_case.execute_command("/chronicle -update", state)
    
    assert "atualizado" in msg.lower()
    mock_llm.generate_text.assert_awaited_once()
    mock_repo.append_milestones.assert_called_once_with(
        "Aventura", 
        "- O herói derrotou o Rei Golem.\n- A chave de cristal foi recuperada."
    )

@pytest.mark.asyncio
async def test_view_chronicle(mock_repo, mock_llm):
    """Testa a leitura do arquivo .md para ser exibido na HUD."""
    mock_repo.read_chronicle.return_value = "- O herói derrotou o Rei Golem."
    use_case = ChronicleManagerUseCase(chronicle_repository=mock_repo, llm_adapter=mock_llm)
    state = SaveState(campaign_name="Aventura", context_buffer=[], active_tags=[])
    
    msg = await use_case.execute_command("/chronicle -view", state)
    
    assert "DIÁRIO DE MARCOS" in msg
    assert "Rei Golem" in msg
    mock_repo.read_chronicle.assert_called_once_with("Aventura")