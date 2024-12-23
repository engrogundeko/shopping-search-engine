from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

from schema import product

class FilterAttributes(BaseModel):
    features: Optional[List[str]] = None
    category: Optional[str] = None

class PriceFilter(BaseModel):
    max: Optional[float] = None
    min: Optional[float] = None

class SearchFilter(BaseModel):
    price: Optional[PriceFilter] = None
    attributes: Optional[FilterAttributes] = None

class SearchRequest(BaseModel):
    search_query: str = Field(..., description="Main search query")
    filter: Optional[SearchFilter] = None
    n_k: int = Field(default=10, ge=1, le=50, description="Number of results to return")
    description: Optional[str] = Field(None, description="Additional search description")
    mode: str = Field(default="search", description="Search mode")
    query: Optional[str] = None
    cache_ttl: int = Field(default=3600, description="Cache time to live in seconds")

class Metadata(BaseModel):
    title: str
    price: float
    discount: Optional[float]
    product_url: str
    image_url: str

class SearchResult(BaseModel):
    content: str
    metadata: Metadata

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    search_query: str
    processing_time: Optional[float] = None