import pytest
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock
from src.adapters.save_repository import JsonSaveRepository
from src.use_cases.load_manager import LoadManager
from src.domain.save_state import SaveState

@pytest.fixture
def temp_load_dir(tmp_path):
    dir_path = tmp_path / "saves"
    dir_path.mkdir()
    
    save_file = dir_path / "aventura_teste.json"
    mock_data = {
        "campaign_name": "Reino de Valéria",
        "context_buffer": ["A taberna estava cheia."],
        "active_tags": ["@taberneiro"]
    }
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
        
    return dir_path

@pytest.mark.asyncio
async def test_load_campaign_success(temp_load_dir):
    repo = JsonSaveRepository(base_data_path=temp_load_dir)
    
    # Criando Mocks isolados para satisfazer o construtor (Épico 35)
    mock_vram = MagicMock()
    mock_vram.force_clear_vram = AsyncMock()
    mock_rag = MagicMock()
    
    manager = LoadManager(repo, mock_vram, mock_rag)
    
    # Executa o comando de load (agora assíncrono)
    result_msg, state = await manager.execute_load("/load aventura_teste")
    
    assert "com sucesso" in result_msg.lower()
    assert state is not None
    assert state.campaign_name == "Reino de Valéria"
    assert "@taberneiro" in state.active_tags

@pytest.mark.asyncio
async def test_load_campaign_not_found(temp_load_dir):
    repo = JsonSaveRepository(base_data_path=temp_load_dir)
    
    # Mocks vazios
    mock_vram = MagicMock()
    mock_vram.force_clear_vram = AsyncMock()
    mock_rag = MagicMock()
    
    manager = LoadManager(repo, mock_vram, mock_rag)
    
    result_msg, state = await manager.execute_load("/load save_fantasma")
    
    assert "não foi encontrado" in result_msg.lower()
    assert state is None