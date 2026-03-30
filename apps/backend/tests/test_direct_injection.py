import pytest
from unittest.mock import MagicMock
from src.use_cases.direct_injection_manager import DirectInjectionUseCase

def test_execute_injection_success():
    """
    Testa se o comando /insert extrai o texto corretamente e o guarda no RAG.
    """
    mock_rag = MagicMock()
    mock_rag.save_memory.return_value = True
    
    use_case = DirectInjectionUseCase(rag_adapter=mock_rag)
    
    command = "/insert O artefato mágico está escondido no poço da vila."
    response_msg = use_case.execute_injection(command)
    
    # Validações
    mock_rag.save_memory.assert_called_once_with("O artefato mágico está escondido no poço da vila.")
    assert "injetado com sucesso" in response_msg.lower()

def test_execute_injection_empty_payload():
    """
    Se o utilizador digitar apenas '/insert', o sistema deve avisar do erro
    em vez de guardar uma string vazia.
    """
    use_case = DirectInjectionUseCase(rag_adapter=MagicMock())
    
    response_msg = use_case.execute_injection("/insert   ")
    
    assert "formato inválido" in response_msg.lower()