import pytest
from src.use_cases.input_processor import InputProcessorUseCase
from src.domain.player_input import ParsedInput

def test_parse_multimodal_input_preserves_order():
    """
    Testa os Requisitos 8.1 e 8.2: O parser deve identificar as ações e falas
    e mantê-las na ordem correta, formatando-as para a LLM.
    """
    processor = InputProcessorUseCase()
    
    # Input do jogador simulando uma jogada complexa
    raw_text = '> Eu abro a porta com um chute. "Tem alguém aí?" > Saco a minha espada.'
    
    parsed = processor.parse_raw_input(raw_text)
    
    assert len(parsed.narrative_blocks) == 3
    assert parsed.narrative_blocks[0] == "[AÇÃO] Eu abro a porta com um chute."
    assert parsed.narrative_blocks[1] == '[FALA] "Tem alguém aí?"'
    assert parsed.narrative_blocks[2] == "[AÇÃO] Saco a minha espada."
    assert not parsed.system_overrides
    assert not parsed.feedback_notes

def test_parse_multimodal_input_extracts_system_blocks():
    """
    Testa o Requisito 8.3: Extração de Trapaças ($) e Feedbacks (#).
    Esses blocos não devem se misturar com a narrativa do personagem.
    """
    processor = InputProcessorUseCase()
    
    raw_text = '> Ataco o goblin. $ O goblin tropeça e cai. # Seja mais descritivo no sangue.'
    
    parsed = processor.parse_raw_input(raw_text)
    
    assert len(parsed.narrative_blocks) == 1
    assert parsed.narrative_blocks[0] == "[AÇÃO] Ataco o goblin."
    
    # Verifica se os blocos de sistema foram extraídos corretamente
    assert len(parsed.system_overrides) == 1
    assert parsed.system_overrides[0] == "O goblin tropeça e cai."
    
    assert len(parsed.feedback_notes) == 1
    assert parsed.feedback_notes[0] == "Seja mais descritivo no sangue."

def test_parse_input_without_prefixes():
    """
    Se o jogador esquecer de colocar prefixos, o sistema deve assumir 
    que é uma [AÇÃO] narrativa padrão para não quebrar o jogo.
    """
    processor = InputProcessorUseCase()
    raw_text = "Eu ando até a taverna e peço uma cerveja."
    
    parsed = processor.parse_raw_input(raw_text)
    
    assert len(parsed.narrative_blocks) == 1
    assert parsed.narrative_blocks[0] == "[AÇÃO] Eu ando até a taverna e peço uma cerveja."

def test_parse_input_exceeds_character_limit():
    """
    Testa o Requisito 33.2: O sistema deve rejeitar inputs que ultrapassem
    o limite configurado no .env (ou injetado no construtor para o teste).
    """
    # Forçamos um limite minúsculo (10 caracteres) apenas para o teste
    processor = InputProcessorUseCase(max_chars=10)
    
    with pytest.raises(ValueError, match="ultrapassou o limite máximo"):
        processor.parse_raw_input("Um texto incrivelmente longo que o jogador tentou enviar para crashar o motor.")

def test_parse_input_within_character_limit():
    """Garante que textos dentro do limite passam normalmente."""
    processor = InputProcessorUseCase(max_chars=100)
    parsed = processor.parse_raw_input("> Ataco!")
    
    assert len(parsed.narrative_blocks) == 1