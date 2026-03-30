import pytest
from unittest.mock import MagicMock
from src.use_cases.map_manager import MapManagerUseCase
from src.domain.save_state import SaveState
from src.domain.map_state import MapNode

@pytest.fixture
def mock_image_adapter():
    # Mock para o futuro adaptador do ComfyUI
    adapter = MagicMock()
    adapter.generate_map_assets.return_value = ("path/to/tile.png", "path/to/icon.png")
    return adapter

def test_map_discover_new_location(mock_image_adapter):
    """Testa a descoberta de um novo local e a criação da primeira ligação."""
    use_case = MapManagerUseCase(image_adapter=mock_image_adapter)
    state = SaveState(campaign_name="Aventura", context_buffer=[], active_tags=[])
    
    # 1. Descobrir primeiro local (Origem)
    msg1 = use_case.execute_command('/map discover "Vila Inicial" "Planície"', state)
    assert "descoberto" in msg1.lower()
    assert len(state.atlas.nodes) == 1
    assert state.atlas.current_location_id == state.atlas.nodes[0].id
    
    # 2. Viajar e descobrir segundo local (Destino)
    msg2 = use_case.execute_command('/map discover "Floresta Negra" "Floresta Densa"', state)
    assert "floresta negra" in msg2.lower()
    assert len(state.atlas.nodes) == 2
    
    # O current_location deve ter mudado para a Floresta
    assert state.atlas.current_location_id == state.atlas.nodes[1].id
    
    # O sistema deve ter criado uma ligação (trilha narrativa) automaticamente
    assert len(state.atlas.connections) == 1
    assert state.atlas.connections[0].from_node_id == state.atlas.nodes[0].id
    assert state.atlas.connections[0].to_node_id == state.atlas.nodes[1].id

def test_map_travel_to_known_location(mock_image_adapter):
    """Testa a movimentação do jogador para um local que já existe no mapa."""
    use_case = MapManagerUseCase(image_adapter=mock_image_adapter)
    
    node1 = MapNode(id="n1", name="Caverna", biome="Pedra")
    node2 = MapNode(id="n2", name="Castelo", biome="Planície")
    
    state = SaveState(
        campaign_name="Aventura", 
        context_buffer=[], 
        active_tags=[],
    )
    state.atlas.nodes.extend([node1, node2])
    state.atlas.current_location_id = "n1" # Jogador está na Caverna
    
    msg = use_case.execute_command('/map travel "Castelo"', state)
    
    assert "viajou para" in msg.lower()
    assert state.atlas.current_location_id == "n2" # Jogador moveu-se para o Castelo
    
    # Deve criar uma trilha da Caverna para o Castelo
    assert len(state.atlas.connections) == 1
    assert state.atlas.connections[0].from_node_id == "n1"