import pytest
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.image_generator import ImageGeneratorUseCase
from src.domain.image_generation import ImageGenerationResponse
from src.domain.save_state import SaveState

@pytest.fixture
def mock_comfyui_adapter():
    adapter = MagicMock()
    adapter.generate_image = AsyncMock(return_value=ImageGenerationResponse(
        success=True, 
        image_path="/output/cena_1.png"
    ))
    return adapter

@pytest.mark.asyncio
async def test_generate_scene_image_success(mock_comfyui_adapter):
    """Testa a geração básica de uma cena."""
    use_case = ImageGeneratorUseCase(comfyui_adapter=mock_comfyui_adapter)
    state = SaveState(campaign_name="Odisseia", context_buffer=[], active_tags=[])
    
    scene_description = "Uma floresta escura com árvores retorcidas."
    
    response = await use_case.generate_scene_image(scene_description, state)
    
    assert response.success is True
    assert response.image_path == "/output/cena_1.png"
    
    # Verifica se o adaptador foi chamado com os parâmetros corretos
    mock_comfyui_adapter.generate_image.assert_awaited_once()
    request_sent = mock_comfyui_adapter.generate_image.call_args[0][0]
    
    # CORREÇÃO: Verifica se a descrição está incluída no prompt enriquecido
    assert scene_description in request_sent.prompt
    assert "masterpiece" in request_sent.prompt
    assert len(request_sent.loras) == 0

@pytest.mark.asyncio
async def test_generate_image_with_lora_and_ip_adapter(mock_comfyui_adapter):
    """
    Testa os Requisitos 5.2 e 5.3: Injeção de LoRA por @tag e 
    passagem de imagem de referência.
    """
    use_case = ImageGeneratorUseCase(comfyui_adapter=mock_comfyui_adapter)
    
    # Simulamos que a última imagem gerada no estado foi salva numa variável fictícia
    # e que o @goblin está na cena.
    state = SaveState(
        campaign_name="Odisseia", 
        context_buffer=[], 
        active_tags=["goblin"]
    )
    # Adicionando um campo dinâmico apenas para simular o armazenamento do último path
    state.last_image_path = "/output/cena_anterior.png" 
    
    # Mock do PresetRepository para simular que o @goblin tem uma LoRA associada
    mock_preset_repo = MagicMock()
    mock_preset_repo.get_lora_for_entity.return_value = "goblin_v1.safetensors"
    use_case.preset_repository = mock_preset_repo

    response = await use_case.generate_scene_image("Um goblin a rir-se.", state)
    
    request_sent = mock_comfyui_adapter.generate_image.call_args[0][0]
    
    assert response.success is True
    assert "goblin_v1.safetensors" in request_sent.loras # Requisito 5.3 (LoRA)
    assert request_sent.reference_image_path == "/output/cena_anterior.png" # Requisito 5.2 (IP-Adapter)