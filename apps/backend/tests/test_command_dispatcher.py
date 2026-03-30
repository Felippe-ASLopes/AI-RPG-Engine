import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.command_dispatcher import CommandDispatcherUseCase

@pytest.fixture
def mock_save():
    return MagicMock()

@pytest.fixture
def mock_load():
    return AsyncMock()

@pytest.fixture
def mock_export():
    return AsyncMock()

@pytest.fixture
def mock_injection():
    return MagicMock()

@pytest.fixture
def mock_delete():
    return MagicMock()

@pytest.fixture
def mock_undo():
    return AsyncMock()

@pytest.fixture
def mock_regen():
    return MagicMock()

@pytest.fixture
def mock_quest():
    return MagicMock()

@pytest.fixture
def mock_hud():
    return MagicMock()

@pytest.fixture
def mock_hud():
    return MagicMock()

@pytest.fixture
def mock_chronicle():
    return AsyncMock()

@pytest.fixture
def mock_map():
    return MagicMock()

@pytest.fixture
def mock_web_search():
    return AsyncMock()

@pytest.fixture
def dispatcher(mock_save, mock_load, mock_export, mock_injection, mock_delete, mock_undo, mock_regen, mock_quest, mock_hud, mock_chronicle, mock_map, mock_web_search):
    """
    Instância centralizada do roteador. 
    Se o construtor do CommandDispatcherUseCase sofrer alterações no futuro, 
    basta atualizar as dependências apenas nesta função.
    """
    return CommandDispatcherUseCase(
        save_manager=mock_save,
        load_manager=mock_load,
        entity_export=mock_export,
        direct_injection=mock_injection,
        delete_manager=mock_delete,
        undo_manager=mock_undo,
        regen_manager=mock_regen,
        quest_manager=mock_quest,
        hud_manager=mock_hud,
        chronicle_manager=mock_chronicle,
        map_manager=mock_map,
        web_search_manager=mock_web_search
    )

@pytest.mark.asyncio
async def test_dispatch_save_command(dispatcher, mock_save):
    mock_save.execute_save.return_value = "[SISTEMA] Jogo salvo."
    
    response = await dispatcher.dispatch("/save aventura1", current_state=MagicMock())
    
    assert response.is_command is True
    assert "[SISTEMA] Jogo salvo." in response.message
    mock_save.execute_save.assert_called_once()

@pytest.mark.asyncio
async def test_dispatch_entity_export_command(dispatcher, mock_export):
    mock_export.execute_extraction.return_value = "[SISTEMA] Entidade salva."
    
    # O dispatcher deve saber que /save -e vai para o export, não para o save normal
    response = await dispatcher.dispatch("/save -e @goblin", current_state=MagicMock())
    
    assert response.is_command is True
    mock_export.execute_extraction.assert_awaited_once()

@pytest.mark.asyncio
async def test_dispatch_direct_injection_command(dispatcher, mock_injection):
    mock_injection.execute_injection.return_value = "[SISTEMA] Facto injetado com sucesso."
    
    response = await dispatcher.dispatch("/insert O rei é um traidor.", current_state=MagicMock())
    
    assert response.is_command is True
    mock_injection.execute_injection.assert_called_once()

@pytest.mark.asyncio
async def test_dispatch_delete_save_command(dispatcher, mock_delete):
    mock_delete.execute_delete.return_value = "[SISTEMA] Save deletado."
    
    current_state = MagicMock()
    response = await dispatcher.dispatch("/save -d meu_save", current_state)
    
    assert response.is_command is True
    mock_delete.execute_delete.assert_called_once_with("/save -d meu_save", current_state)
    assert "Save deletado" in response.message

@pytest.mark.asyncio
async def test_dispatch_delete_preset_command(dispatcher, mock_delete):
    mock_delete.execute_delete.return_value = "[SISTEMA] Preset deletado."
    
    response = await dispatcher.dispatch("/save -deletepreset @ogro", current_state=MagicMock())
    
    assert response.is_command is True
    mock_delete.execute_delete.assert_called_once()
    assert "Preset deletado" in response.message

@pytest.mark.asyncio
async def test_dispatch_undo_command_success(dispatcher, mock_undo):
    """Garante que o comando << aciona o rollback e devolve o input para edição."""
    mock_undo.execute_undo.return_value = ("[SISTEMA] Ação desfeita.", MagicMock(), "> Ação que me arrependi.")
    
    current_state = MagicMock()
    current_state.campaign_name = "Odisseia_Espacial"
    
    response = await dispatcher.dispatch("<<", current_state)
    
    assert response.is_command is True
    assert "[SISTEMA] Ação desfeita." in response.message
    # Verifica a recuperação do texto para o HUD (Épico 21)
    assert response.restored_input == "> Ação que me arrependi." 
    mock_undo.execute_undo.assert_awaited_once_with("Odisseia_Espacial")

@pytest.mark.asyncio
async def test_dispatch_undo_command_no_active_campaign(dispatcher):
    """Garante a trava de segurança se o jogador utilizar << no menu inicial."""
    # Passando current_state como None
    response = await dispatcher.dispatch("<<", current_state=None)
    
    assert response.is_command is True
    assert "Nenhuma campanha ativa" in response.message

@pytest.mark.asyncio
async def test_dispatch_invalid_command(dispatcher):
    response = await dispatcher.dispatch("/comando_inexistente", current_state=MagicMock())
    
    assert response.is_command is True
    assert "Comando desconhecido" in response.message

@pytest.mark.asyncio
async def test_dispatch_not_a_command(dispatcher):
    # Input normal de narrativa, não deve ser tratado como comando do sistema
    response = await dispatcher.dispatch("> Eu ataco o orc.", current_state=MagicMock())
    
    assert response.is_command is False

@pytest.mark.asyncio
async def test_dispatch_regen_command(dispatcher, mock_regen):
    mock_regen.execute_regen.return_value = ("[SISTEMA] Gerando nova resposta...", MagicMock(), "TEXT")
    
    response = await dispatcher.dispatch("/regen -t", current_state=MagicMock())
    
    assert response.is_command is True
    assert response.regen_type == "TEXT"
    mock_regen.execute_regen.assert_called_once()

@pytest.mark.asyncio
async def test_dispatch_quest_command(dispatcher, mock_quest):
    """Garante que o comando /quest é roteado para o QuestManager."""
    mock_quest.execute_command.return_value = "[SISTEMA] Intenção adicionada."
    
    current_state = MagicMock()
    
    response = await dispatcher.dispatch("/quest -a -i roubar a chave do guarda", current_state)
    
    assert response.is_command is True
    assert "Intenção adicionada" in response.message
    mock_quest.execute_command.assert_called_once_with("/quest -a -i roubar a chave do guarda", current_state)

@pytest.mark.asyncio
async def test_dispatch_hud_command(dispatcher, mock_hud):
    """Garante que o comando /hud é roteado corretamente para o HudManager."""
    mock_hud.execute_command.return_value = "[SISTEMA] Status HP atualizado para 50."
    
    current_state = MagicMock()
    
    # Simula um comando silencioso enviado pelo Frontend para reduzir a vida
    response = await dispatcher.dispatch("/hud stat hp 50", current_state)
    
    assert response.is_command is True
    assert "Status HP atualizado" in response.message
    
    # Verifica se o método correto foi chamado com os argumentos corretos
    mock_hud.execute_command.assert_called_once_with("/hud stat hp 50", current_state)

@pytest.mark.asyncio
async def test_dispatch_chronicle_command(dispatcher, mock_chronicle):
    mock_chronicle.execute_command.return_value = "[SISTEMA] Diário atualizado."
    current_state = MagicMock()
    
    response = await dispatcher.dispatch("/chronicle -u", current_state)
    
    assert response.is_command is True
    assert "atualizado" in response.message
    mock_chronicle.execute_command.assert_awaited_once_with("/chronicle -u", current_state)

@pytest.mark.asyncio
async def test_dispatch_map_command(dispatcher, mock_map):
    mock_map.execute_command.return_value = "[SISTEMA] Novo local descoberto e mapeado: 'Caverna'."
    current_state = MagicMock()
    
    response = await dispatcher.dispatch('/map discover "Caverna" "Gelo"', current_state)
    
    assert response.is_command is True
    assert "descoberto" in response.message
    mock_map.execute_command.assert_called_once_with('/map discover "Caverna" "Gelo"', current_state)

@pytest.mark.asyncio
async def test_dispatch_search_command(dispatcher, mock_web_search):
    mock_web_search.execute_command.return_value = "[WEB] Resultados encontrados."
    response = await dispatcher.dispatch("/search história do brasil", current_state=MagicMock())
    
    assert response.is_command is True
    assert "Resultados encontrados" in response.message
    mock_web_search.execute_command.assert_awaited_once()