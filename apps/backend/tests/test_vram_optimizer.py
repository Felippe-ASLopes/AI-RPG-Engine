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