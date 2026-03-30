import pytest
from unittest.mock import MagicMock, AsyncMock
from src.domain.save_state import SaveState
from src.domain.undo_snapshot import UndoSnapshot
from src.use_cases.undo_manager import UndoManagerUseCase

@pytest.fixture
def mock_undo_repo():
    return MagicMock()

@pytest.fixture
def mock_vram_optimizer():
    vram = MagicMock()
    vram.force_clear_vram = AsyncMock()
    return vram

@pytest.mark.asyncio
async def test_save_turn_to_undo_buffer(mock_undo_repo, mock_vram_optimizer):
    """Testa se o estado antes do turno é salvo corretamente no repositório."""
    use_case = UndoManagerUseCase(mock_undo_repo, mock_vram_optimizer)
    
    state = SaveState(campaign_name="Odisseia", context_buffer=["Turno 1"], active_tags=[])
    user_input = "> Eu abro a porta."
    
    use_case.save_turn(state, user_input)
    
    mock_undo_repo.save_snapshot.assert_called_once()
    saved_campaign, saved_snapshot = mock_undo_repo.save_snapshot.call_args[0]
    
    assert saved_campaign == "Odisseia"
    assert saved_snapshot.last_user_input == "> Eu abro a porta."
    assert saved_snapshot.state.context_buffer == ["Turno 1"]

@pytest.mark.asyncio
async def test_execute_undo_success(mock_undo_repo, mock_vram_optimizer):
    """
    Testa o fluxo de rollback (Épico 11) e a recuperação do input 
    para o HUD (Épico 21), garantindo a limpeza da VRAM.
    """
    use_case = UndoManagerUseCase(mock_undo_repo, mock_vram_optimizer)
    
    # Simula o repositório devolvendo o último snapshot
    fake_state = SaveState(campaign_name="Odisseia", context_buffer=["Turno 1"], active_tags=[])
    fake_snapshot = UndoSnapshot(state=fake_state, last_user_input="> Ação que me arrependi.")
    mock_undo_repo.pop_last_snapshot.return_value = fake_snapshot
    
    msg, restored_state, restored_input = await use_case.execute_undo("Odisseia")
    
    # O VRAM Optimizer DEVE ser acionado para a IA "esquecer" o futuro descartado
    mock_vram_optimizer.force_clear_vram.assert_awaited_once()
    
    assert "retrocedeu" in msg.lower()
    assert restored_state is not None
    assert restored_input == "> Ação que me arrependi."

@pytest.mark.asyncio
async def test_execute_undo_empty_buffer(mock_undo_repo, mock_vram_optimizer):
    """Garante que o sistema não quebra se o jogador tentar dar undo no primeiro turno."""
    use_case = UndoManagerUseCase(mock_undo_repo, mock_vram_optimizer)
    
    mock_undo_repo.pop_last_snapshot.return_value = None
    
    msg, restored_state, restored_input = await use_case.execute_undo("Odisseia")
    
    mock_vram_optimizer.force_clear_vram.assert_not_called()
    assert "não há ações" in msg.lower()
    assert restored_state is None
    assert restored_input == ""