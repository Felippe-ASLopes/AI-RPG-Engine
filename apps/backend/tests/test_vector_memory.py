import pytest
from src.adapters.vector_memory import VectorMemoryAdapter

def test_vector_memory_add_and_recall():
    rag = VectorMemoryAdapter(db_path="../../../../data/chromadb_test")
    
    rag.add_memory("test_1", "O cavaleiro perdeu sua espada no lago.")
    resultados = rag.recall_memories("Onde está a arma do guerreiro?", n_results=1)
    
    assert len(resultados) > 0
    assert "espada" in resultados[0].lower()