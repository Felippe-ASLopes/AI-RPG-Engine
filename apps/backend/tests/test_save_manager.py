import pytest
import os
from pathlib import Path
from src.domain.save_state import SaveState
from src.adapters.save_repository import JsonSaveRepository
from src.use_cases.save_manager import SaveManager

@pytest.fixture
def temp_save_dir(tmp_path):
    return str(tmp_path)

def test_save_campaign_success(temp_save_dir):
    repo = JsonSaveRepository(base_data_path=temp_save_dir)
    manager = SaveManager(repo)
    state = SaveState(campaign_name="valeria", context_buffer=["Turno 1: O rei caiu."], active_tags=["@rei"])
    
    result_msg = manager.execute_save("!save aventura1", state)
    
    assert "com sucesso" in result_msg.lower()
    assert os.path.exists(Path(temp_save_dir) / "aventura1.json")

def test_save_campaign_overwrite_blocked(temp_save_dir):
    repo = JsonSaveRepository(base_data_path=temp_save_dir)
    manager = SaveManager(repo)
    state = SaveState(campaign_name="valeria", context_buffer=[], active_tags=[])
    
    # Primeiro save
    manager.execute_save("!save aventura1", state)
    
    # Tenta salvar por cima sem a flag
    result_msg = manager.execute_save("!save aventura1", state)
    assert "já existe" in result_msg.lower()

def test_save_campaign_overwrite_success(temp_save_dir):
    repo = JsonSaveRepository(base_data_path=temp_save_dir)
    manager = SaveManager(repo)
    state = SaveState(campaign_name="valeria", context_buffer=[], active_tags=[])
    
    manager.execute_save("!save aventura1", state)
    
    # Salva com a flag de sobrescrever
    result_msg = manager.execute_save("!save --overwrite aventura1", state)
    assert "com sucesso" in result_msg.lower()