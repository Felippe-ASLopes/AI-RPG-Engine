import pytest
from unittest.mock import MagicMock
from src.use_cases.quest_manager import QuestManagerUseCase
from src.domain.save_state import SaveState
from src.domain.quest import Quest

@pytest.fixture
def mock_rag():
    return MagicMock()

def test_add_quest_success(mock_rag):
    """Testa a nova sintaxe de flags para adição."""
    use_case = QuestManagerUseCase(rag_adapter=mock_rag)
    state = SaveState(campaign_name="Aventura", context_buffer=[], active_tags=[])
    
    # Novo formato solicitado: /quest -a -i [texto]
    msg = use_case.execute_command('/quest -a -i roubar chave @guarda', state)
    
    assert "adicionada" in msg.lower()
    assert len(state.quest_log) == 1
    assert state.quest_log[0].quest_type == "INTENTION"
    assert "roubar chave" in state.quest_log[0].description
    assert "guarda" in state.quest_log[0].related_tags

def test_complete_quest_moves_to_rag(mock_rag):
    """Testa a nova sintaxe de conclusão e valida a string traduzida."""
    mock_rag.save_memory.return_value = True
    use_case = QuestManagerUseCase(rag_adapter=mock_rag)

    quest = Quest(id="q123", quest_type="OBJECTIVE", description="Salvar a princesa.")
    state = SaveState(campaign_name="Aventura", context_buffer=[], active_tags=[], quest_log=[quest])

    # Novo formato solicitado: /quest -c [id]
    msg = use_case.execute_command('/quest -c q123', state)

    assert "concluído" in msg.lower()
    assert len(state.quest_log) == 0

    mock_rag.save_memory.assert_called_once()
    saved_text = mock_rag.save_memory.call_args[0][0]
    
    # CORREÇÃO: Variável escrita corretamente (saved_text)
    assert "Salvar a princesa." in saved_text
    assert "[OBJETIVO CONCLUÍDO]" in saved_text