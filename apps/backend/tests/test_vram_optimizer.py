import pytest
from src.use_cases.vram_optimizer import VRAMOptimizer

@pytest.mark.asyncio
async def test_vram_swap_to_image():
    optimizer = VRAMOptimizer()
    assert optimizer.get_current_state() == "TEXT"
    
    await optimizer.swap_to_image_mode()
    assert optimizer.get_current_state() == "IMAGE"

@pytest.mark.asyncio
async def test_vram_swap_to_text():
    optimizer = VRAMOptimizer()
    await optimizer.swap_to_image_mode()
    await optimizer.swap_to_text_mode()
    assert optimizer.get_current_state() == "TEXT"

@pytest.mark.asyncio
async def test_vram_force_clear():
    """
    (Épico 35) Testa a rotina de expurgo forçado da placa de vídeo.
    Garante que a VRAM volta ao controle do motor principal após a limpeza.
    """
    optimizer = VRAMOptimizer()
    
    # Forçamos a máquina a ir para o estado de gerar imagens
    await optimizer.swap_to_image_mode()
    assert optimizer.get_current_state() == "IMAGE"
    
    # Acionamos o botão de pânico/limpeza (usado no load)
    await optimizer.force_clear_vram()
    
    # A VRAM deve ser devolvida para o motor de texto após o flush
    assert optimizer.get_current_state() == "TEXT"