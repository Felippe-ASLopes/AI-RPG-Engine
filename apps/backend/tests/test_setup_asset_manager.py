import pytest
from unittest.mock import MagicMock
from src.use_cases.setup_asset_manager import SetupAssetManagerUseCase

def test_save_character_asset_success():
    """
    Testa o fluxo de upload de uma imagem de personagem.
    O nome deve ser higienizado e a extensão preservada.
    """
    mock_bridge = MagicMock()
    # Simula o adaptador retornando o caminho final
    mock_bridge.save_entity_image.return_value = "data/Assets/Characters/sir_lancelot.png"
    
    use_case = SetupAssetManagerUseCase(asset_bridge=mock_bridge)
    
    # Dados simulados do upload
    fake_image_bytes = b"fake_png_data"
    entity_name = "Sir Lancelot!" # Nome com espaços e símbolos
    
    result_path = use_case.save_asset(
        entity_name=entity_name, 
        category="Characters", 
        image_bytes=fake_image_bytes, 
        extension=".png"
    )
    
    # O Caso de Uso deve ter limpado o nome antes de mandar pro adaptador
    mock_bridge.save_entity_image.assert_called_once_with(
        "sir_lancelot", "Characters", fake_image_bytes, ".png"
    )
    assert result_path == "data/Assets/Characters/sir_lancelot.png"

def test_save_asset_invalid_category():
    """
    Garante que não seja possível salvar imagens fora do padrão arquitetural do Atlas Local.
    """
    use_case = SetupAssetManagerUseCase(asset_bridge=MagicMock())
    
    with pytest.raises(ValueError, match="Categoria inválida"):
        use_case.save_asset("Espada", "Weapons", b"data", ".jpg")