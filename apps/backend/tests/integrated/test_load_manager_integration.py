import pytest
from unittest.mock import MagicMock, AsyncMock
from src.use_cases.load_manager import LoadManager
from src.domain.save_state import SaveState

@pytest.mark.asyncio
async def test_load_manager_clears_vram_and_rag_on_success():
    """
    Testa se o LoadManager orquestra corretamente as chamadas para a GPU (VRAM)
    e para o Banco de Dados Vetorial (ChromaDB) durante o hot-swap (Épico 35).
    """
    
    # 1. Mock do Repositório (Simula que o arquivo .json foi encontrado no SSD)
    mock_repo = MagicMock()
    fake_state = SaveState(campaign_name="Cyber_City", context_buffer=[], active_tags=[])
    mock_repo.load.return_value = fake_state
    
    # 2. Mock do Otimizador de VRAM (Simula a API de hardware)
    mock_vram = MagicMock()
    mock_vram.force_clear_vram = AsyncMock() # Porque o método no LoadManager sofreu await
    
    # 3. Mock do Banco Vetorial (Simula o ChromaDB)
    mock_rag = MagicMock()
    mock_rag.switch_campaign_collection = MagicMock()
    
    # Instancia o manager com os mocks injetados
    manager = LoadManager(
        repository=mock_repo,
        vram_optimizer=mock_vram,
        rag_adapter=mock_rag
    )
    
    # Executa o comando
    result_msg, state = await manager.execute_load("/load cyberpunk_save")
    
    # Asserções de Integração: O "Coração" do Épico 35
    
    # A VRAM foi mandada limpar?
    mock_vram.force_clear_vram.assert_awaited_once()
    
    # O RAG trocou a "pasta" de memórias para a campanha correta ('Cyber_City')?
    mock_rag.switch_campaign_collection.assert_called_once_with("Cyber_City")
    
    # O carregamento final reportou sucesso?
    assert state is not None
    assert state.campaign_name == "Cyber_City"
    assert "carregado com sucesso" in result_msg.lower()

@pytest.mark.asyncio
async def test_load_manager_does_not_clear_if_save_not_found():
    """
    Garante que não apagamos a memória da VRAM atual se o usuário
    digitar um nome de arquivo de save que não existe.
    """
    mock_repo = MagicMock()
    mock_repo.load.return_value = None # Arquivo não achado
    
    mock_vram = MagicMock()
    mock_vram.force_clear_vram = AsyncMock()
    
    mock_rag = MagicMock()
    
    manager = LoadManager(mock_repo, mock_vram, mock_rag)
    
    await manager.execute_load("/load save_fantasma")
    
    # Como o save falhou, a VRAM e o RAG da sessão atual DEVEM ser preservados
    mock_vram.force_clear_vram.assert_not_called()
    mock_rag.switch_campaign_collection.assert_not_called()