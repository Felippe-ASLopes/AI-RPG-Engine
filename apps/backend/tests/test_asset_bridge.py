import pytest
from src.adapters.asset_bridge import AssetBridgeAdapter

def test_asset_bridge_missing_entity():
    bridge = AssetBridgeAdapter()
    # Entidade que não existe deve retornar string vazia
    context = bridge.get_entity_metadata("EntidadeFantasma", category="Characters")
    assert context == ""