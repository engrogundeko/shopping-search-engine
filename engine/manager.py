from .search.query_engine import QueryEngine
from .cache.redis import RedisCache

class SearchEngineManager:
    """
    Manages search engine operations with integrated caching.
    """

    def __init__(self, search_engine: QueryEngine, cache_manager: RedisCache):
        self.search_engine = search_engine
        self.cache_manager = cache_manager

    async def search(self, search_query:str, query, mode='quality', cache_ttl=3600):
        """
        Perform a search with caching.
        - Check cache for results before executing the search.
        - Save results to cache for future use.
        """
        cached_results = self.cache_manager.get(query)
        if cached_results:
            print("Cache hit for query:", query)
            return cached_results

        print("Cache miss for query:", query)

        results = await self.search_engine.asearch(search_query,query, mode)
        await self.cache_manager.set(query, results, ttl=cache_ttl)
        return results

manager = SearchEngineManager(QueryEngine(), RedisCache())

if __name__ == '__main__':
    import asyncio
    asyncio.run(manager.search("Lenovo Laptop", "Lenovo", "fast")) 
