import pytest
from unittest.mock import MagicMock
from src.use_cases.cheat_manager import CheatManagerUseCase
from src.domain.player_input import ActiveCheats

def test_add_cheat_success():
    """Testa a adição de uma nova trapaça ou regra de mundo."""
    mock_repo = MagicMock()
    mock_repo.load_cheats.return_value = ActiveCheats(active_overrides=[])
    mock_repo.save_cheats.return_value = True

    use_case = CheatManagerUseCase(cheat_repository=mock_repo)
    result = use_case.add_cheat("Sou completamente imune a qualquer tipo de magia.")

    assert "sucesso" in result.lower()
    mock_repo.save_cheats.assert_called_once()
    
    saved_cheats = mock_repo.save_cheats.call_args[0][0]
    assert "Sou completamente imune a qualquer tipo de magia." in saved_cheats.active_overrides

def test_get_persistent_cheat_context():
    """Testa a formatação rigorosa para a LLM aceitar a trapaça como verdade."""
    mock_repo = MagicMock()
    mock_repo.load_cheats.return_value = ActiveCheats(
        active_overrides=["Eu tenho ouro infinito na mochila."]
    )
    use_case = CheatManagerUseCase(cheat_repository=mock_repo)

    context = use_case.get_persistent_context()
    
    assert "[FATOS IMPOSTOS PELO JOGADOR" in context
    assert "- Eu tenho ouro infinito na mochila." in context

def test_get_persistent_cheat_context_empty():
    """Se o jogador jogar limpo, não gasta tokens da LLM."""
    mock_repo = MagicMock()
    mock_repo.load_cheats.return_value = ActiveCheats()
    use_case = CheatManagerUseCase(cheat_repository=mock_repo)

    assert use_case.get_persistent_context() == ""