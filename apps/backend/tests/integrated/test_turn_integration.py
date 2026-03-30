import pytest
from unittest.mock import MagicMock, AsyncMock
from src.use_cases.input_processor import InputProcessorUseCase
from src.use_cases.feedback_manager import FeedbackManagerUseCase
from src.domain.player_input import PlayerPreferences

@pytest.mark.asyncio
async def test_turn_orchestrator_saves_feedback_from_input():
    """
    Testa se o feedback (#) digitado pelo jogador no meio da ação
    é extraído pelo InputProcessor e salvo pelo FeedbackManager.
    """
    # 1. Setup dos Casos de Uso
    input_processor = InputProcessorUseCase(max_chars=2000)
    
    mock_prefs_repo = MagicMock()
    mock_prefs_repo.load_preferences.return_value = PlayerPreferences()
    mock_prefs_repo.save_preferences.return_value = True
    feedback_manager = FeedbackManagerUseCase(preferences_repository=mock_prefs_repo)
    
    # 2. Input multimodal do jogador
    raw_text = '> Eu ataco o orc com minha espada. # Pare de descrever o sangue de forma tão gráfica.'
    
    # 3. Simulação do fluxo do Controlador (FastAPI)
    parsed_input = input_processor.parse_raw_input(raw_text)
    
    # O Orquestrador identifica que há feedbacks e os salva
    if parsed_input.feedback_notes:
        for note in parsed_input.feedback_notes:
            feedback_manager.add_feedback(note, category="tone")
            
    # 4. Asserções de Integração
    assert len(parsed_input.narrative_blocks) == 1
    assert len(parsed_input.feedback_notes) == 1
    
    # Verifica se o FeedbackManager foi acionado corretamente com o texto extraído
    mock_prefs_repo.save_preferences.assert_called_once()
    saved_prefs = mock_prefs_repo.save_preferences.call_args[0][0]
    assert "Pare de descrever o sangue de forma tão gráfica." in saved_prefs.tone_corrections