import pytest
from unittest.mock import MagicMock
from src.use_cases.entity_tagging_manager import EntityTaggingUseCase
from src.domain.player_input import ParsedInput

def test_extract_and_inject_tags_mixed_sources():
    """
    Testa se o sistema deteta múltiplas tags, procura no Atlas primeiro e,
    se não encontrar, recorre ao banco vetorial (RAG).
    """
    mock_asset_bridge = MagicMock()
    mock_rag = MagicMock()
    
    # Simula o Atlas Local a encontrar o Rei, mas a falhar na Espada
    def mock_get_metadata(name, category):
        if name == "rei_arthur":
            return "[ATLAS LOCAL - CHARACTERS] rei_arthur\nDescrição: O grande rei."
        return ""
    mock_asset_bridge.get_entity_metadata.side_effect = mock_get_metadata
    
    # Simula o RAG a encontrar a Espada, já que o Atlas falhou
    def mock_recall(query, n_results):
        if "espada chamas" in query:
            return ["A espada de chamas queima tudo em redor."]
        return []
    mock_rag.recall_memories.side_effect = mock_recall
    
    use_case = EntityTaggingUseCase(
        asset_bridge=mock_asset_bridge, 
        rag_adapter=mock_rag
    )
    
    # Simulando o input processado vindo do Épico 8
    parsed_input = ParsedInput(
        narrative_blocks=["[AÇÃO] Eu ataco o @rei_arthur com a minha @espada_chamas."]
    )
    
    injected_context = use_case.process_tags(parsed_input)
    
    # Validações
    assert "rei_arthur" in injected_context
    assert "O grande rei." in injected_context
    assert "ESPADA_CHAMAS" in injected_context  # <-- Alterado para maiúsculas
    assert "A espada de chamas queima" in injected_context
    
    # Verifica que a ordem de prioridade de chamadas foi respeitada
    assert mock_asset_bridge.get_entity_metadata.call_count > 0
    mock_rag.recall_memories.assert_called_once()

def test_process_tags_no_tags_found():
    """Se o input não contiver @tags, deve retornar uma string vazia rapidamente."""
    use_case = EntityTaggingUseCase(MagicMock(), MagicMock())
    parsed_input = ParsedInput(narrative_blocks=["[AÇÃO] Apenas ando pela floresta normal."])
    
    assert use_case.process_tags(parsed_input) == ""