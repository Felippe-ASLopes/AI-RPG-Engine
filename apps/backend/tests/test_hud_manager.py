import pytest
from src.use_cases.hud_manager import HudManagerUseCase
from src.domain.save_state import SaveState

def test_hud_update_stats_success():
    """Testa a alteração de atributos numéricos (HP, Mana, Level)."""
    use_case = HudManagerUseCase()
    state = SaveState(campaign_name="Aventura", context_buffer=[], active_tags=[])
    
    # O HP inicial padrão é 100. Vamos reduzir para 45.
    msg = use_case.execute_command("/hud stat hp 45", state)
    
    assert "atualizado para 45" in msg.lower()
    assert state.stats.hp == 45

def test_hud_add_inventory_item():
    """Testa a inserção de um novo item no inventário."""
    use_case = HudManagerUseCase()
    state = SaveState(campaign_name="Aventura", context_buffer=[], active_tags=[])
    
    msg = use_case.execute_command('/hud item add "Poção de Cura" 2', state)
    
    assert "adicionado" in msg.lower()
    assert len(state.inventory) == 1
    assert state.inventory[0].name == "Poção de Cura"
    assert state.inventory[0].quantity == 2

def test_hud_remove_inventory_item():
    """Testa a remoção de um item pelo nome exato."""
    use_case = HudManagerUseCase()
    state = SaveState(campaign_name="Aventura", context_buffer=[], active_tags=[])
    
    # Adiciona primeiro
    use_case.execute_command('/hud item add "Espada Longa" 1', state)
    assert len(state.inventory) == 1
    
    # Remove
    msg = use_case.execute_command('/hud item remove "Espada Longa"', state)
    
    assert "removido" in msg.lower()
    assert len(state.inventory) == 0