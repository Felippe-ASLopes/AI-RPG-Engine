import pytest
from src.domain.campaign_setup import ContentGating
from src.use_cases.content_gating_manager import ContentGatingUseCase

def test_build_system_constraints_all_blocked():
    """
    Testa se as instruções restritivas são geradas corretamente quando
    o jogador desativa Gore, NSFW e adiciona temas banidos.
    """
    gating = ContentGating(
        allow_nsfw=False,
        allow_gore=False,
        banned_topics=["aranhas", "tortura"]
    )
    
    use_case = ContentGatingUseCase()
    constraints_prompt = use_case.build_system_constraints(gating)
    
    # Verifica se os comandos de bloqueio estão no prompt
    assert "sexual explícito" in constraints_prompt
    assert "violência gráfica extrema" in constraints_prompt
    assert "aranhas, tortura" in constraints_prompt

def test_build_system_constraints_all_allowed():
    """
    Se o jogador for +18 e permitir tudo, o prompt restritivo deve ser vazio 
    para economizar tokens da LLM.
    """
    gating = ContentGating(
        allow_nsfw=True,
        allow_gore=True,
        banned_topics=[]
    )
    
    use_case = ContentGatingUseCase()
    constraints_prompt = use_case.build_system_constraints(gating)
    
    assert constraints_prompt == ""

def test_validate_llm_output_success():
    """
    Testa uma resposta limpa da LLM que passa pela Blacklist.
    """
    gating = ContentGating(banned_topics=["aranhas gigantes"])
    use_case = ContentGatingUseCase()
    
    output = "O herói entrou na caverna e encontrou um baú de ouro."
    is_valid, _ = use_case.validate_llm_output(output, gating)
    
    assert is_valid is True

def test_validate_llm_output_triggers_regen():
    """
    Testa o Sanity Check (Requisito 25.2). Se a LLM falar algo banido, 
    devemos detetar para forçar o /regen.
    """
    gating = ContentGating(banned_topics=["aranha", "veneno"])
    use_case = ContentGatingUseCase()
    
    output = "De repente, uma ARANHA enorme desceu do teto!"
    
    is_valid, violated_term = use_case.validate_llm_output(output, gating)
    
    assert is_valid is False
    assert violated_term == "aranha"