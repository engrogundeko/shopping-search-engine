from typing import final
import httpx


class ShopEngine:
    def __init__(self, search_query):
        self.cache = {}
        self.search_results = []
        self.search_query = search_query 
        self.client: httpx.AsyncClient = httpx.AsyncClient()

    async def close(self):
        await self.client.aclose()


