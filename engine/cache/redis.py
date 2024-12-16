import redis
import json
from .base import CacheBase
from ...config import REDIS_PASSWORD

class RedisCache(CacheBase):
    """
    Redis-based caching system.
    """

    def __init__(self, 
    host='redis-10198.c228.us-central1-1.gce.redns.redis-cloud.com', 
    port=10198, 
    db=0):
        self.host = host
        self.port = port
        self.db = db
        self.client = redis.Redis(host=self.host, port=self.port, db=self.db, password=REDIS_PASSWORD, username="default")

    # def connect(self):
    #     self.client = redis.Redis(host=self.host, port=self.port, db=self.db)

    async def set(self, key, value, ttl=None):
        """
        Asynchronously store a key-value pair with optional TTL (time-to-live).
        """
        try:
            # Convert value to JSON string
            json_value = json.dumps(value)
            self.client.set(key, json_value, ex=ttl)
        except Exception as e:
            print(f"Error setting cache: {e}")
            # Fallback to storing raw value if JSON conversion fails
            self.client.set(key, str(value), ex=ttl)

    def get(self, key):
        """
        Retrieve a value by key.
        Returns None if the key does not exist.
        """
        cached_value = self.client.get(key)
        if cached_value is None:
            return None
        try:
            return json.loads(cached_value)
        except (TypeError, json.JSONDecodeError):
            # If JSON decoding fails, return the raw value
            return cached_value

    def delete(self, key):
        """
        Delete a key from the cache.
        """
        self.client.delete(key)

    def clear(self):
        """
        Clear all keys from the cache.
        """
        self.client.flushdb()
