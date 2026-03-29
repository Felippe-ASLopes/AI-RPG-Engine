import pytest
from unittest.mock import MagicMock
from src.use_cases.preset_manager import PresetManagerUseCase
from src.domain.campaign_setup import CampaignSetup, EntityAttributes, Milestone

def test_auto_save_campaign_template():
    """
    Testa o Requisito 23.3: Geração automática do ficheiro .template
    ao finalizar o Assistente de Criação.
    """
    mock_repo = MagicMock()
    use_case = PresetManagerUseCase(preset_repository=mock_repo)
    
    setup = CampaignSetup(
        campaign_name="Odisseia Espacial",
        theme="Ficção Científica",
        main_character=EntityAttributes(
            name="Comandante Shepard", appearance="Armadura N7", personality="Líder",
            power_skill="Biótica", benefits="Carisma", flaws="Teimoso"
        )
    )
    
    use_case.auto_save_template(setup)
    
    # O repositório deve ter sido chamado para guardar o ficheiro com a extensão .template
    mock_repo.save_template.assert_called_once_with("odisseia_espacial", setup)

def test_export_nested_presets():
    """
    Testa o Requisito 23.1: Hierarquia de Presets. 
    Ao receber uma campanha completa, deve conseguir desmembrar e guardar os NPCs.
    """
    mock_repo = MagicMock()
    use_case = PresetManagerUseCase(preset_repository=mock_repo)
    
    setup = CampaignSetup(
        campaign_name="Reino de Valéria",
        theme="Fantasia Medieval",
        main_character=EntityAttributes(name="Arthur", appearance="...", personality="...", power_skill="...", benefits="...", flaws="..."),
        companions=[
            EntityAttributes(name="Merlin", appearance="Velho", personality="Sábio", power_skill="Magia", benefits="Imortal", flaws="Críptico")
        ],
        rivals=[
            EntityAttributes(name="Morgana", appearance="Bruxa", personality="Vingativa", power_skill="Feitiçaria", benefits="Ilusão", flaws="Arrogante")
        ]
    )
    
    use_case.export_nested_presets(setup)
    
    # Deve guardar o companheiro e o rival individualmente
    assert mock_repo.save_entity_preset.call_count == 2
    
    # Verifica os argumentos das chamadas
    calls = mock_repo.save_entity_preset.call_args_list
    assert calls[0][0][0] == "merlin"
    assert calls[1][0][0] == "morgana"

def test_import_entity_preset_success():
    """
    Testa o Requisito 23.2: Cross-Campaign Loading de um NPC guardado anteriormente.
    """
    mock_repo = MagicMock()
    # Simula o repositório a devolver um dicionário do NPC
    mock_repo.load_entity_preset.return_value = {
        "name": "Merlin", "appearance": "Velho", "personality": "Sábio",
        "power_skill": "Magia", "benefits": "Imortal", "flaws": "Críptico"
    }
    
    use_case = PresetManagerUseCase(preset_repository=mock_repo)
    
    npc = use_case.import_entity_preset("merlin")
    
    assert isinstance(npc, EntityAttributes)
    assert npc.name == "Merlin"
    assert npc.power_skill == "Magia"