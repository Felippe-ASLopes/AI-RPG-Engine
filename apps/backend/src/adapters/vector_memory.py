import chromadb
import uuid
from chromadb.utils import embedding_functions
from pathlib import Path
from src.infrastructure.logger import get_logger
from src.infrastructure.config import AppConfig

logger = get_logger("VECTOR_MEMORY")

class VectorMemoryAdapter:
    """
    Gerencia a Memória de Longo Prazo do RPG utilizando ChromaDB (Épico 4).
    Armazena e recupera vetores de contexto para criar a sensação de um mundo vivo.
    """
    def __init__(self, db_path: Path = AppConfig.CHROMA_DB_PATH):
        self.chroma_path = db_path
        
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
    
    def switch_campaign_collection(self, campaign_name: str):
        """
        (Épico 35) Isola o contexto RAG mudando a collection ativa para a campanha carregada.
        Isso previne que a IA puxe memórias de outro save.
        """
        # Sanitiza o nome para o ChromaDB (letras minúsculas, números e underscores)
        safe_name = "".join(c if c.isalnum() else "_" for c in campaign_name).strip("_").lower()
        if not safe_name:
            safe_name = "default_campaign"

        collection_name = f"campaign_{safe_name}"

        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.emb_fn
            )
            logger.info(f"RAG: Banco vetorial isolado. Collection ativa: '{collection_name}'.")
        except Exception as e:
            logger.error(f"RAG: Erro ao isolar memórias para {campaign_name}: {str(e)}")

    def recall_exact_match(self, keyword_query: str, n_results: int = 3) -> list:
        """
        Épico 10: Procura por 'exact match' ou palavra-chave (Filtro 'where_document' do ChromaDB),
        ignorando a similaridade vetorial para garantir precisão absoluta.
        """
        try:
            # O operador $contains procura a substring exata dentro da memória guardada
            results = self.collection.query(
                query_texts=[keyword_query],
                n_results=n_results,
                where_document={"$contains": keyword_query}
            )
            
            documents = results.get("documents", [[]])[0]
            
            if documents:
                logger.info(f"RAG Exact Match: {len(documents)} memórias recuperadas para '{keyword_query}'.")
            else:
                logger.debug(f"RAG Exact Match: Nenhuma ocorrência exata de '{keyword_query}' encontrada.")
                
            return documents
            
        except Exception as e:
            logger.error(f"Erro ao forçar recuperação no RAG: {str(e)}")
            return []

    def save_memory(self, memory_text: str, metadata: dict = None) -> bool:
        """
        Épico 16: Guarda um facto diretamente no banco vetorial da campanha atual.
        """
        try:
            # O ChromaDB exige IDs únicos para cada documento
            unique_id = uuid.uuid4().hex
            
            # Se não houver metadados, criamos um dicionário vazio ou uma tag de injeção manual
            meta = metadata if metadata else {"source": "manual_injection"}
            
            self.collection.add(
                documents=[memory_text],
                metadatas=[meta],
                ids=[unique_id]
            )
            
            logger.info(f"Nova memória guardada no RAG (ID: {unique_id}): '{memory_text[:30]}...'")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao guardar memória no ChromaDB: {str(e)}")
            return False
        
    def delete_campaign_collection(self, campaign_name: str) -> bool:
        """
        (Épico 38) Apaga permanentemente todas as memórias vetoriais de uma campanha.
        """
        safe_name = "".join(c if c.isalnum() else "_" for c in campaign_name).strip("_").lower()
        if not safe_name:
            safe_name = "default_campaign"

        collection_name = f"campaign_{safe_name}"

        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"RAG: Banco vetorial '{collection_name}' deletado com sucesso.")
            return True
        except ValueError:
            logger.warning(f"RAG: A collection '{collection_name}' não existia para ser deletada.")
            return False
        except Exception as e:
            logger.error(f"RAG: Erro ao deletar collection '{collection_name}': {str(e)}")
            return False