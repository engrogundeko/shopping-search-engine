import json
from typing import List, Optional, Dict, Any
import httpx
from utils.logging import logger
from utils.decorator import async_retry
from config import GOOGLE_SEARCH_API_KEY, GOOGLE_SEARCH_ID

class GoogleSearchTool:
    """A tool for performing Google Custom Search using their API"""
    
    def __init__(self):
        self.api_key = GOOGLE_SEARCH_API_KEY
        self.search_engine_id = GOOGLE_SEARCH_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    @async_retry(retries=3, delay=1.0)
    async def search(
        self,
        query: str,
        num_results: int = 5,
        search_type: Optional[str] = None,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Perform a Google search using the Custom Search API.
        
        Args:
            query: The search query string
            num_results: Number of results to return (max 10)
            search_type: Type of search ('image' for image search)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            List of search results, each containing relevant information
        """
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)  # API limit is 10
            }
            
            if search_type:
                params['searchType'] = search_type
                
            # Add any additional parameters
            params.update(kwargs)
            
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if 'error' in data:
                    error_msg = data['error'].get('message', 'Unknown error in Google Search API')
                    logger.error(f"Google Search API error: {error_msg}")
                    return []
                
                # Extract and format results
                results = []
                for item in data.get('items', []):
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'google'
                    }
                    
                    # Add image-specific fields if present
                    if search_type == 'image':
                        image = item.get('image', {})
                        result.update({
                            'thumbnail': image.get('thumbnailLink', ''),
                            'image_url': item.get('link', ''),
                            'image_height': image.get('height', 0),
                            'image_width': image.get('width', 0)
                        })
                    
                    results.append(result)
                
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during Google search: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error performing Google search: {str(e)}")
            return []
    
    @async_retry(retries=3, delay=1.0)
    async def search_images(
        self,
        query: str,
        num_results: int = 5,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Perform a Google image search.
        
        Args:
            query: The search query string
            num_results: Number of results to return (max 10)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            List of image search results
        """
        return await self.search(
            query,
            num_results=num_results,
            search_type='image',
            **kwargs
        )
    
    @async_retry(retries=2, delay=1.0)
    async def search_products(
        self,
        query: str,
        num_results: int = 5,
        **kwargs: Any
    ) -> List[Dict[str, Any]]:
        """
        Perform a product-focused search by adding relevant terms.
        
        Args:
            query: The search query string
            num_results: Number of results to return (max 10)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            List of product search results
        """
        # Enhance query for product search
        product_query = f"{query} product review price"
        results = await self.search(
            product_query,
            num_results=num_results,
            **kwargs
        )
        
        # Process results to extract product information
        processed_results = []
        for result in results:
            # Try to extract price if present in snippet
            snippet = result.get('snippet', '').lower()
            price = None
            
            # Simple price extraction (can be enhanced)
            if '$' in snippet:
                try:
                    price_text = snippet[snippet.index('$'):].split()[0]
                    price = float(price_text.replace('$', '').replace(',', ''))
                except (ValueError, IndexError):
                    pass
            
            processed_result = {
                **result,
                'price': price,
                'type': 'product'
            }
            processed_results.append(processed_result)
        
        return processed_results


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_search():
        search_tool = GoogleSearchTool()
        
        # Test regular search
        results = await search_tool.search("Python programming")
        print("Regular search results:", json.dumps(results, indent=2))
        
        # Test image search
        image_results = await search_tool.search_images("cute cats")
        print("Image search results:", json.dumps(image_results, indent=2))
        
        # Test product search
        product_results = await search_tool.search_products("iPhone 15")
        print("Product search results:", json.dumps(product_results, indent=2))
    
    asyncio.run(test_search())
