import pytest
from unittest.mock import MagicMock
from src.use_cases.forced_recall_manager import ForcedRecallUseCase
from src.domain.player_input import ParsedInput

def test_forced_recall_success():
    """
    Testa se o sistema pega nas queries forçadas (*), acede ao RAG 
    com pesquisa exata e formata o bloco de injeção.
    """
    mock_rag = MagicMock()
    # Simula o RAG a encontrar o texto exato
    mock_rag.recall_exact_match.return_value = ["O mercenário traiu o rei por 50 moedas de ouro."]
    
    use_case = ForcedRecallUseCase(rag_adapter=mock_rag)
    
    parsed_input = ParsedInput(
        narrative_blocks=["> Eu pergunto ao guarda sobre a traição."],
        forced_queries=["o mercenário traiu o rei"]
    )
    
    injected_context = use_case.process_forced_queries(parsed_input)
    
    # Validações
    mock_rag.recall_exact_match.assert_called_once_with("o mercenário traiu o rei", n_results=2)
    assert "MEMÓRIAS RECUPERADAS MANUALMENTE" in injected_context
    assert "O mercenário traiu o rei por 50 moedas de ouro." in injected_context

def test_forced_recall_no_results():
    """Se o RAG não encontrar a memória, deve avisar a IA discretamente."""
    mock_rag = MagicMock()
    mock_rag.recall_exact_match.return_value = []
    
    use_case = ForcedRecallUseCase(rag_adapter=mock_rag)
    parsed_input = ParsedInput(forced_queries=["a espada fantasma"])
    
    injected_context = use_case.process_forced_queries(parsed_input)
    
    assert "Nenhum registo exato encontrado" in injected_context