from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time

from engine.manager import SearchEngineManager
from engine.search.query_engine import QueryEngine
from engine.cache.redis import RedisCache

# Initialize the search engine manager
manager = SearchEngineManager(QueryEngine(), RedisCache())

# Create FastAPI app
router = APIRouter(
    
)

# Request model for search
class SearchRequest(BaseModel):
    search_query: str
    query: Optional[str] = None
    mode: str = 'fast'
    cache_ttl: int = 3600

# Response model for search results
class SearchResponse(BaseModel):
    results: List[dict]
    total_results: int
    search_query: str
    mode: str
    time: float

@router.post("/search", response_model=SearchResponse)
async def perform_search(request: SearchRequest):
    """
    Perform a search across multiple providers.
    
    Args:
    - search_query: Main search query
    - query: Optional refined query for semantic search
    - mode: Search mode ('fast', 'balanced', 'quality')
    - cache_ttl: Time to live for cached results
    
    Returns:
    - Search results with metadata
    """
    try:
        # Use the query parameter if not provided, default to search_query
        refined_query = request.query or request.search_query
        
        # Perform the search
        time1 = time.time()
        results = await manager.search(
            search_query=request.search_query, 
            query=refined_query, 
            mode=request.mode,
            cache_ttl=request.cache_ttl
        )
        time2 = time.time()
        
        # Prepare response
        return {
            "results": results,
            "total_results": len(results),
            "search_query": request.search_query,
            "mode": request.mode,   
            "time": time2-time1
        }
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

# Optional: Health check endpoint
@router.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify API is running.
    """
    return {"status": "healthy"}

# If running this file directly, use uvicorn to start the server
