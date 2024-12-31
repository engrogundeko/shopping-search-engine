from typing import List, Dict, Optional, Any

from utils.logging import logger
from config import SEARXNG_BASE_URL
from langchain.docstore.document import Document
from utils.decourator import async_retry

import httpx


class SearxNGSearchTool:
    """A tool for performing searches using the SearxNG API with enhanced search syntax support."""
    
    def __init__(self):

        self.base_url = SEARXNG_BASE_URL
    
    @async_retry(retries=3, delay=1.0)
    async def search(
        self,
        query: str,
        num_results: int = 5,
        categories: Optional[str] = None,
        engines: Optional[str] = None,
        language: Optional[str] = None,
        time_range: Optional[str] = None,
        format_: Optional[str] = 'json',
        results_on_new_tab: Optional[int] = 0,
        image_proxy: Optional[bool] = None,
        safesearch: Optional[int] = 1,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Perform a search using the SearxNG API with customizable parameters and search syntax support.
        
        Args:
            query: The search query string.
            num_results: Number of results to return.
            categories: Comma-separated list of search categories (optional).
            engines: Comma-separated list of search engines to use (optional).
            language: The language code for the search results (optional).
            time_range: Time range for search (optional: [day, month, year]).
            format_: Output format (json, csv, rss).
            results_on_new_tab: Whether to open results in a new tab (0 or 1).
            image_proxy: Whether to proxy image results (optional).
            safesearch: Safe search filter (0, 1, or 2).
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            A list of search results with relevant information.
        """
        try:
            # Handle engine/category modifiers (e.g., !wp, !images)
            if query.startswith('!'):
                categories, engines, query = self._process_bangs(query)
            
            # Handle language modifiers (e.g., :fr, :en)
            if query.startswith(':'):
                language, query = self._process_language(query)
            else:
                language = language  # fallback to default language parameter if needed

            # Handle external bangs (e.g., !!wikipedia)
            if query.startswith('!!'):
                return await self._handle_external_bang(query)
            
            # Build the parameters for the search request
            params = {
                'q': query,
                'num': num_results,  # Adjusting to the API limit
                'categories': categories,
                'engines': engines,
                'language': language,
                'time_range': time_range,
                'format': format_,
                'results_on_new_tab': results_on_new_tab,
                'image_proxy': image_proxy,
                'safesearch': safesearch,
                **kwargs  # Additional parameters if any
            }

            # Clean up any None parameters
            params = {k: v for k, v in params.items() if v is not None}
            
            async with httpx.AsyncClient() as client:
                # Send GET request to SearxNG /search endpoint
                response = await client.get(self.base_url + "/search", params=params)
                response.raise_for_status()
                
                data = response.json()

                # If the response has an error, log it and return an empty list
                if 'error' in data:
                    error_msg = data['error'].get('message', 'Unknown error in SearxNG API')
                    logger.error(f"SearxNG API error: {error_msg}")
                    return []
                
                # Extract and format results
                results = []
                for item in data.get('results', []):
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('url', ''),
                        'snippet': item.get('content', ''),
                        'source': item.get('engine', 'searxng')
                    }
                    
                    results.append(
                        Document(
                            metadata=result,
                            page_content=result['snippet']
                        )
                    )
                logger.info(f"Number of search results: {len(results)}")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during SearxNG search: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error performing SearxNG search: {str(e)}")
            return []

    def _process_bangs(self, query: str):
        """Process and return categories and engines based on bangs."""
        categories = None
        engines = None

        # Parse the bang syntax
        parts = query[1:].split(' ', 1)
        if len(parts) > 1:
            categories, engines = parts
        else:
            categories = parts[0]

        return categories, engines, query

    def _process_language(self, query: str):
        """Process and return language from language modifier."""
        lang = query[1:3]  # First two characters after colon
        query = query[3:].strip()  # Remove language modifier from query
        return lang, query
    
    async def _handle_external_bang(self, query: str):
        """Handle external bangs like !!wikipedia or !!duckduckgo."""
        external_query = query[2:].strip()
        # Directly redirect to the external query's result (e.g., DuckDuckGo, Wikipedia, etc.)
        # You may perform a request or return a special result here.
        # For simplicity, redirecting to the first result directly.
        return {"redirect": f"External search: {external_query}"}
    
    @async_retry(retries=3, delay=1.0)
    async def search_images(
        self,
        query: str,
        num_results: int = 5,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Perform an image search using the SearxNG API.
        
        Args:
            query: The search query string.
            num_results: Number of results to return.
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            A list of image search results.
        """
        return await self.search(
            query,
            num_results=num_results,
            categories="images", 
            **kwargs
        )
    
    @async_retry(retries=3, delay=1.0)
    async def search_videos(
        self,
        query: str,
        num_results: int = 5,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Perform a search for videos using the SearxNG API.
        
        Args:
            query: The search query string.
            num_results: Number of results to return.
            **kwargs: Additional parameters to pass to the API.
            
        Returns:
            A list of video search results.
        """
        return await self.search(
            query,
            num_results=num_results,
            categories="videos", 
            **kwargs
        )
