import pytest
from src.use_cases.regen_manager import RegenManagerUseCase
from src.domain.save_state import SaveState

def test_execute_regen_text_success():
    """Garante que o comando /regen -t remove a última resposta da IA do buffer."""
    use_case = RegenManagerUseCase()
    
    # Simulando um buffer onde a IA respondeu por último
    state = SaveState(
        campaign_name="Odisseia",
        context_buffer=[
            "[AÇÃO] Eu abro a porta.",
            "Atrás da porta, um goblin salta em sua direção rugindo!" # Resposta da IA
        ],
        active_tags=[]
    )
    
    msg, new_state, regen_type = use_case.execute_regen("/regen -t", state)
    
    assert regen_type == "TEXT"
    assert "descartada" in msg.lower()
    # O buffer agora só deve ter o input do jogador!
    assert len(new_state.context_buffer) == 1
    assert new_state.context_buffer[0] == "[AÇÃO] Eu abro a porta."

def test_execute_regen_text_blocks_if_last_is_player():
    """Garante que não apagamos o input do jogador acidentalmente."""
    use_case = RegenManagerUseCase()
    
    state = SaveState(
        campaign_name="Odisseia",
        context_buffer=[
            "Atrás da porta, um goblin salta em sua direção rugindo!",
            "[AÇÃO] Eu ataco o goblin com a espada." # Input do jogador
        ],
        active_tags=[]
    )
    
    msg, new_state, regen_type = use_case.execute_regen("/regen -text", state)
    
    assert regen_type == "NONE"
    assert "não é possível regerar" in msg.lower()
    assert len(new_state.context_buffer) == 2 # O buffer não foi alterado

def test_execute_regen_image_success():
    """Garante que a regeneração de imagem não altera o buffer de texto."""
    use_case = RegenManagerUseCase()
    
    state = SaveState(
        campaign_name="Odisseia",
        context_buffer=["Atrás da porta, um goblin salta!"],
        active_tags=[]
    )
    
    msg, new_state, regen_type = use_case.execute_regen("/regen -img", state)
    
    assert regen_type == "IMAGE"
    assert "nova imagem" in msg.lower()
    assert len(new_state.context_buffer) == 1 # Intacto