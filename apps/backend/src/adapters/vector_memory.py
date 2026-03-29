import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from src.infrastructure.logger import get_logger

logger = get_logger("VECTOR_MEMORY")

class VectorMemoryAdapter:
    """
    Gerencia a Memória de Longo Prazo do RPG utilizando ChromaDB (Épico 4).
    Armazena e recupera vetores de contexto para criar a sensação de um mundo vivo.
    """
    def __init__(self, db_path: str = "../../../../data/chromadb"):
        current_dir = Path(__file__).parent
        self.chroma_path = (current_dir / db_path).resolve()
        
        logger.info(f"Inicializando Banco Vetorial (RAG) em: {self.chroma_path}")
        self._ensure_directory()
        
        self.client = chromadb.PersistentClient(path=str(self.chroma_path))
        
        # Incremento: Utilizando um modelo multilíngue nativo para entender Português
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        # Aplicamos a função de embedding na nossa collection
        self.collection = self.client.get_or_create_collection(
            name="campaign_memories",
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.emb_fn
        )

    def _ensure_directory(self):
        self.chroma_path.mkdir(parents=True, exist_ok=True)

    def add_memory(self, memory_id: str, text: str, metadata: dict = None):
        try:
            self.collection.add(
                documents=[text],
                metadatas=[metadata or {"type": "event"}],
                ids=[memory_id]
            )
            logger.debug(f"Memória registrada: [{memory_id}]")
        except Exception as e:
            logger.error(f"Erro ao salvar memória vetorial: {str(e)}")

    def recall_memories(self, query: str, n_results: int = 3) -> list:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = results.get("documents", [[]])[0]
            
            if documents:
                logger.info(f"RAG: {len(documents)} memórias recuperadas para a pesquisa.")
            else:
                logger.debug("RAG: Nenhuma memória relevante encontrada para o contexto.")
                
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao recuperar memórias do RAG: {str(e)}")
            return []