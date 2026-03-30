import pytest
from unittest.mock import MagicMock
from src.use_cases.feedback_manager import FeedbackManagerUseCase
from src.domain.player_input import PlayerPreferences

def test_add_tone_feedback_success():
    """Testa a adição de uma nova correção de tom narrativo."""
    mock_repo = MagicMock()
    # Simula um arquivo JSON vazio
    mock_repo.load_preferences.return_value = PlayerPreferences(tone_corrections=[], mechanic_rules=[])
    mock_repo.save_preferences.return_value = True

    use_case = FeedbackManagerUseCase(preferences_repository=mock_repo)
    result = use_case.add_feedback("Seja mais descritivo no sangue.", "tone")

    assert "sucesso" in result.lower()
    mock_repo.save_preferences.assert_called_once()
    
    # Verifica se o texto foi adicionado à entidade antes de salvar
    saved_prefs = mock_repo.save_preferences.call_args[0][0]
    assert "Seja mais descritivo no sangue." in saved_prefs.tone_corrections

def test_get_persistent_context():
    """Testa a formatação (Tarefa 7.2) do bloco a ser injetado na LLM."""
    mock_repo = MagicMock()
    # Simula preferências já salvas no disco
    mock_repo.load_preferences.return_value = PlayerPreferences(
        tone_corrections=["Mais sombrio e gótico."],
        mechanic_rules=["Sempre role os dados para mim."]
    )
    use_case = FeedbackManagerUseCase(preferences_repository=mock_repo)

    context = use_case.get_persistent_context()
    
    # Verifica se os cabeçalhos obrigatórios do Domínio estão presentes
    assert "[PREFERÊNCIAS DO JOGADOR" in context
    assert "Correções de Tom Narrativo:" in context
    assert "- Mais sombrio e gótico." in context
    assert "Regras e Mecânicas:" in context
    assert "- Sempre role os dados para mim." in context

def test_get_persistent_context_empty():
    """Se não houver preferências, não deve gerar bloco de texto (poupar tokens)."""
    mock_repo = MagicMock()
    mock_repo.load_preferences.return_value = PlayerPreferences()
    use_case = FeedbackManagerUseCase(preferences_repository=mock_repo)

    context = use_case.get_persistent_context()
    assert context == ""