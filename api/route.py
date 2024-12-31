import time
from typing import Literal
import numpy as np

from schema.apis import SearchRequest, SearchResponse, WebSearchRequest
from fastapi import APIRouter, HTTPException

from engine.manager import SearchEngineManager
from engine.search.query_engine import QueryEngine
from engine.cache.redis import RedisCache
from providers.web.manager import web_manager

# Initialize the search engine manager
manager = SearchEngineManager(QueryEngine(), RedisCache())

# Create FastAPI app
router = APIRouter()

def preprocess_results(data):
    if isinstance(data, np.generic):  # Handle numpy scalars
        return data.item()
    elif isinstance(data, dict):  # Handle nested dictionaries
        return {key: preprocess_results(value) for key, value in data.items()}
    elif isinstance(data, list):  # Handle lists
        return [preprocess_results(item) for item in data]
    return data

@router.post("/search/{search_type}")
async def search_engine(
    search_type: Literal["insights", "comparison", "web", "review"], 
    request: WebSearchRequest):
    try:
        # Perform the search
        time1 = time.time()
        results = await web_manager.search(search_type=search_type, **request.__dict__)
        time2 = time.time()

        results = preprocess_results(results)
        
        return {
            "results": results,
            "total_results": len(results),
            "search_query": request.search_query,
            "mode": request.mode,   
            "time": time2-time1
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Search failed: INTERNAL SERVER ERROR"
        )


@router.post("/search", response_model=SearchResponse)
async def perform_search(request: SearchRequest):
    try:
        # Use the query parameter if not provided, default to search_query
        # refined_query = request.query or request.search_query
        
        # Perform the search
        time1 = time.time()
        results = await ...
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
        import traceback
        error_trace = traceback.format_exc()
        print(f"Full Error Traceback:\n{error_trace}")
        raise HTTPException(
            status_code=500, 
            detail=f"Search failed: {str(e)}\n\nFull Traceback: {error_trace}"
        )


# Optional: Health check endpoint
@router.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify API is running.
    """
    return {"status": "healthy"}

# If running this file directly, use uvicorn to start the server
