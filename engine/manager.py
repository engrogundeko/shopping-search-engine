from .cache.redis import RedisCache
from .search.query_engine import QueryEngine

class SearchEngineManager:
    """
    Manages search engine operations with integrated caching.
    """

    def __init__(self, search_engine: QueryEngine, cache_manager: RedisCache):
        self.search_engine = search_engine
        self.cache_manager = cache_manager

    async def search(self, search_query: str, query, mode='fast', cache_ttl=3600):
        """
        Perform a search with caching and save results to a text file.
        - Check cache for results before executing the search.
        - Save results to cache for future use and to a text file.
        """
        import time
        import json

        time1 = time.time()
        
        # Safely retrieve cached results
        results = self.cache_manager.get(query)
        if results is not None:
            print("Cache hit for query:", query)
        else:
            print("Cache miss for query:", query)
            
            # Perform the search
            results = await self.search_engine.asearch(search_query, query, mode)
            
            # Ensure results are not empty before caching or saving
            if results:
                try:
                    # Cache the results
                    await self.cache_manager.set(query, results, ttl=cache_ttl)
                except Exception as e:
                    print(f"Error caching results: {e}")
                
                try:
                    # Save results to a text file
                    file_path = f"{query.replace(' ', '_')}_results.txt"
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(json.dumps(results, indent=4))
                    print(f"Results saved to file: {file_path}")
                except Exception as e:
                    print(f"Error saving results to file: {e}")

        time2 = time.time()
        print(f"Search completed. Results: {len(results)}, Time taken: {time2 - time1:.2f} seconds")
        
        return results


manager = SearchEngineManager(QueryEngine(), RedisCache())

if __name__ == '__main__':
    import asyncio
    asyncio.run(manager.search("Lenovo Laptop", "Best Affordable Laptops", "fast"))
