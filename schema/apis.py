from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


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
    price: float = 0.0
    discount: Optional[float] = 0.0
    image_url: Optional[str] = None
    product_url: Optional[str] = None

    @field_validator('price', mode='before')
    def parse_price(cls, v):
        from providers.jumia.utils import parse_price
        if isinstance(v, str):
            try:
                return parse_price(v)
            except ValueError:
                return 0.0
        return v

    @field_validator('discount', mode='before')
    def parse_discount(cls, v):
        from providers.jumia.utils import parse_discount
        if isinstance(v, str):
            try:
                return parse_discount(v)
            except ValueError:
                return 0.0
        return v

class SearchResult(BaseModel):
    content: str
    metadata: Metadata

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    search_query: str
    processing_time: Optional[float] = None