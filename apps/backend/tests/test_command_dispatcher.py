import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.command_dispatcher import CommandDispatcherUseCase

@pytest.mark.asyncio
async def test_dispatch_save_command():
    mock_save = MagicMock()
    mock_save.execute_save.return_value = "[SISTEMA] Jogo salvo."
    
    dispatcher = CommandDispatcherUseCase(
        save_manager=mock_save, 
        load_manager=AsyncMock(), 
        entity_export=AsyncMock(),
        direct_injection=MagicMock()  # <- Correção: 4º argumento adicionado
    )
    
    response = await dispatcher.dispatch("/save aventura1", current_state=MagicMock())
    
    assert response.is_command is True
    assert "[SISTEMA] Jogo salvo." in response.message
    mock_save.execute_save.assert_called_once()

@pytest.mark.asyncio
async def test_dispatch_entity_export_command():
    mock_export = AsyncMock()
    mock_export.execute_extraction.return_value = "[SISTEMA] Entidade salva."
    
    dispatcher = CommandDispatcherUseCase(
        save_manager=MagicMock(), 
        load_manager=AsyncMock(), 
        entity_export=mock_export,
        direct_injection=MagicMock()  # <- Correção: 4º argumento adicionado
    )
    
    # O dispatcher deve saber que /save -e vai para o export, não para o save normal
    response = await dispatcher.dispatch("/save -e @goblin", current_state=MagicMock())
    
    assert response.is_command is True
    mock_export.execute_extraction.assert_awaited_once()

@pytest.mark.asyncio
async def test_dispatch_direct_injection_command():
    """Testa se o dispatcher roteia corretamente para o /insert (Épico 16)."""
    mock_injection = MagicMock()
    mock_injection.execute_injection.return_value = "[SISTEMA] Facto injetado com sucesso."
    
    dispatcher = CommandDispatcherUseCase(
        save_manager=MagicMock(),
        load_manager=AsyncMock(),
        entity_export=AsyncMock(),
        direct_injection=mock_injection  # <- Passando o mock correto para testar
    )
    
    response = await dispatcher.dispatch("/insert O rei é um traidor.", current_state=MagicMock())
    
    assert response.is_command is True
    mock_injection.execute_injection.assert_called_once()

@pytest.mark.asyncio
async def test_dispatch_invalid_command():
    # Correção: Adicionado o 4º argumento MagicMock()
    dispatcher = CommandDispatcherUseCase(MagicMock(), AsyncMock(), AsyncMock(), MagicMock())
    
    response = await dispatcher.dispatch("/comando_inexistente", current_state=MagicMock())
    
    assert response.is_command is True
    assert "Comando desconhecido" in response.message

@pytest.mark.asyncio
async def test_dispatch_not_a_command():
    # Correção: Adicionado o 4º argumento MagicMock()
    dispatcher = CommandDispatcherUseCase(MagicMock(), AsyncMock(), AsyncMock(), MagicMock())
    
    # Input normal de narrativa
    response = await dispatcher.dispatch("> Eu ataco o orc.", current_state=MagicMock())
    
    # Deve avisar o controlador que isto NÃO é um comando e deve seguir para a IA
    assert response.is_command is False