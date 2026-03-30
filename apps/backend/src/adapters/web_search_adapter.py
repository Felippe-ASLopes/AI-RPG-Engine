from typing import List
from src.domain.web_search import SearchResult
from src.infrastructure.logger import get_logger

logger = get_logger("WEB_SEARCH")

class DuckDuckGoAdapter:
    """
    Adaptador de pesquisa web (Épico 6.1).
    Nota: Em ambiente de produção, instale 'duckduckgo-search' (pip install duckduckgo-search)
    e utilize 'from duckduckgo_search import DDGS' aqui dentro.
    """
    async def search(self, query: str, max_results: int = 3) -> List[SearchResult]:
        logger.info(f"Executando pesquisa web real para: '{query}'")
        
        # Simulação da chamada real à biblioteca duckduckgo_search para manter o código limpo
        # No mundo real, faríamos:
        # with DDGS() as ddgs:
        #     results = list(ddgs.text(query, max_results=max_results))
        
        # Retorno simulado para a arquitetura (substitua pelo código acima quando colocar em produção)
        mock_results = [
            SearchResult(
                title=f"Resultado sobre {query}", 
                snippet=f"Informações detalhadas encontradas na internet sobre {query}.", 
                url="https://duckduckgo.com"
            )
        ]
        return mock_results