from pydantic import BaseModel

class SearchResult(BaseModel):
    """Representa um resultado limpo devolvido pelo motor de busca."""
    title: str
    snippet: str
    url: str