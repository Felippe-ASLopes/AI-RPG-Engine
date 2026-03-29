import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from src.use_cases.campaign_wizard import CampaignWizardUseCase
from src.domain.campaign_setup import CampaignSetup
from src.domain.llm import LLMGenerationResponse

@pytest.mark.asyncio
async def test_generate_campaign_fully_manual_bypasses_llm():
    """
    Se o jogador preencher absolutamente tudo, o Caso de Uso deve apenas validar 
    os dados no Pydantic e não gastar processamento/tempo acionando a LLM.
    """
    mock_llm = AsyncMock()
    use_case = CampaignWizardUseCase(llm_adapter=mock_llm)
    
    full_data = {
        "campaign_name": "A Sombra de Eldoria",
        "theme": "Fantasia Sombria",
        "main_character": {
            "name": "Kaelen",
            "appearance": "Alto, cicatriz no rosto, olhos cinzentos.",
            "personality": "Cinico, mas leal aos amigos.",
            "power_skill": "Magia de sangue.",
            "benefits": "Resistência a veneno.",
            "flaws": "Arrogante e impulsivo."
        },
        "companions": [],
        "rivals": [],
        "milestones": [
            {"title": "O Despertar", "description": "Descobrir o amuleto perdido."}
        ]
    }
    
    setup = await use_case.generate_campaign(full_data)
    
    # A LLM não deve ter sido chamada
    mock_llm.generate_text.assert_not_called()
    assert setup.campaign_name == "A Sombra de Eldoria"
    assert setup.main_character.name == "Kaelen"

@pytest.mark.asyncio
async def test_generate_campaign_partial_data_triggers_llm():
    """
    Se o jogador preencher apenas os dados parciais (ex: Só o nome e o tema),
    o sistema deve acionar a LLM para preencher o resto (Requisito 14.1).
    """
    mock_llm = AsyncMock()
    
    # O jogador só forneceu isso na UI
    partial_data = {
        "campaign_name": "Cyber Neon",
        "theme": "Cyberpunk",
        "main_character": {
            "name": "V",
            "power_skill": "Hackear sistemas."
        }
    }
    
    # Simulando a LLM retornando o JSON completado
    fake_json_response = json.dumps({
        "campaign_name": "Cyber Neon",
        "theme": "Cyberpunk",
        "main_character": {
            "name": "V",
            "appearance": "Jaqueta de couro pesada, braço biônico visível.",
            "personality": "Frio, focado em dinheiro.",
            "power_skill": "Hackear sistemas.",
            "benefits": "Contatos no submundo.",
            "flaws": "Vício em adrenalina."
        },
        "companions": [],
        "rivals": [],
        "milestones": [{"title": "O Primeiro Contrato", "description": "Roubar o chip.", "is_completed": False}]
    })
    
    mock_llm.generate_text.return_value = LLMGenerationResponse(
        content=fake_json_response,
        tokens_used=200
    )
    
    use_case = CampaignWizardUseCase(llm_adapter=mock_llm)
    setup = await use_case.generate_campaign(partial_data)
    
    # A LLM DEVE ter sido chamada para completar
    mock_llm.generate_text.assert_awaited_once()
    
    # O retorno deve preservar o que o jogador digitou...
    assert setup.campaign_name == "Cyber Neon"
    assert setup.main_character.name == "V"
    assert setup.main_character.power_skill == "Hackear sistemas."
    
    # ...E conter o que a IA inventou
    assert setup.main_character.appearance != ""
    assert len(setup.milestones) == 1