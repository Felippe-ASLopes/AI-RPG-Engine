import pytest
from unittest.mock import MagicMock
from src.use_cases.delete_manager import DeleteManagerUseCase
from src.domain.save_state import SaveState

def test_delete_save_success():
    """Testa o fluxo ideal onde um save antigo é deletado e o RAG é limpo."""
    mock_save_repo = MagicMock()
    mock_preset_repo = MagicMock()
    mock_rag = MagicMock()

    # Simula que o arquivo lido pertence a uma campanha diferente da atual
    state_to_delete = SaveState(campaign_name="campanha_antiga", context_buffer=[], active_tags=[])
    mock_save_repo.load.return_value = state_to_delete
    mock_save_repo.delete.return_value = True

    use_case = DeleteManagerUseCase(mock_save_repo, mock_preset_repo, mock_rag)

    # Estado atual simulando a campanha que o jogador está jogando agora
    current_state = SaveState(campaign_name="campanha_atual", context_buffer=[], active_tags=[])

    result_msg = use_case.execute_delete("/save -delete save_velho", current_state)

    # Validações
    assert "expurgados permanentemente" in result_msg.lower()
    mock_rag.delete_campaign_collection.assert_called_once_with("campanha_antiga")
    mock_save_repo.delete.assert_called_once_with("save_velho")

def test_delete_save_active_campaign_blocked():
    """Testa a trava de segurança (Épico 38.3): não pode apagar o save da campanha ativa."""
    mock_save_repo = MagicMock()
    mock_preset_repo = MagicMock()
    mock_rag = MagicMock()

    # O save que ele quer deletar pertence à mesma campanha que está rodando
    state_to_delete = SaveState(campaign_name="campanha_atual", context_buffer=[], active_tags=[])
    mock_save_repo.load.return_value = state_to_delete

    use_case = DeleteManagerUseCase(mock_save_repo, mock_preset_repo, mock_rag)
    current_state = SaveState(campaign_name="campanha_atual", context_buffer=[], active_tags=[])

    result_msg = use_case.execute_delete("/save -d save_recente", current_state)

    # Verifica se bloqueou e se NÃO chamou as funções de deleção físicas
    assert "acesso negado" in result_msg.lower()
    mock_rag.delete_campaign_collection.assert_not_called()
    mock_save_repo.delete.assert_not_called()

def test_delete_preset_success():
    """Garante que a exclusão de presets limpa o nome e chama o repositório correto."""
    mock_save_repo = MagicMock()
    mock_preset_repo = MagicMock()
    mock_rag = MagicMock()

    mock_preset_repo.delete_entity_preset.return_value = True

    use_case = DeleteManagerUseCase(mock_save_repo, mock_preset_repo, mock_rag)

    # current_state não importa para presets
    result_msg = use_case.execute_delete("/save -dp @rei_arthur", current_state=None)

    assert "excluído permanentemente" in result_msg.lower()
    # Verifica se o @ foi removido antes de enviar para o repositório
    mock_preset_repo.delete_entity_preset.assert_called_once_with("rei_arthur")

def test_delete_invalid_format():
    """Garante que comandos pela metade são rejeitados graciosamente."""
    use_case = DeleteManagerUseCase(MagicMock(), MagicMock(), MagicMock())
    
    result_msg = use_case.execute_delete("/save -d", current_state=None)
    
    assert "formato inválido" in result_msg.lower()