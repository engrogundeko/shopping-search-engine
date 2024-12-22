from typing import Optional, List
from pydantic import BaseModel

class FilterAttrubuteSchema(BaseModel):
    features: List[str] | None = []
    category: str | None = ""
    brand_preferences: List[str] | None = []

class FilterSchema(BaseModel):
    price: dict
    attributes : FilterAttrubuteSchema


# Request model for search
class SearchRequest(BaseModel):
    search_query: str
    description: Optional[str] = None
    mode: str = 'fast'
    filter: FilterSchema
    n_k: int

# Response model for search results
class SearchResponse(BaseModel):
    results: List[dict]
    total_results: int
    search_query: str
    mode: str
    time: float