import pytest
from pathlib import Path
from src.adapters.vector_memory import VectorMemoryAdapter

def test_vector_memory_add_and_recall():
    rag = VectorMemoryAdapter(db_path=Path("../../../../data/chromadb_test"))
    
    rag.add_memory("test_1", "O cavaleiro perdeu sua espada no lago.")
    resultados = rag.recall_memories("Onde está a arma do guerreiro?", n_results=1)
    
    assert len(resultados) > 0
    assert "espada" in resultados[0].lower()

def test_switch_campaign_collection_sanitization():
    """
    (Épico 35) Testa se a troca de contexto do RAG higieniza corretamente
    os nomes das campanhas para não quebrar o padrão do ChromaDB.
    """
    rag = VectorMemoryAdapter(db_path=Path("../../../../data/chromadb_test"))
    
    # Teste 1: Nome normal com hífens e números
    rag.switch_campaign_collection("Cyber_Punk-2077")
    # O hífen vira underscore e tudo fica minúsculo
    assert rag.collection.name == "campaign_cyber_punk_2077"
    
    # Teste 2: Símbolos bizarros e espaços
    rag.switch_campaign_collection("  @#Save Vazio..  ")
    assert rag.collection.name == "campaign_save_vazio"
    
    # Teste 3: String vazia ou só de símbolos
    rag.switch_campaign_collection("@@@")
    assert rag.collection.name == "campaign_default_campaign"