import redis
from .base import CacheBase

class RedisCache(CacheBase):
    """
    Redis-based caching system.
    """

    def __init__(self, host='localhost', port=6379, db=0):
        self.host = host
        self.port = port
        self.db = db
        self.client = redis.Redis(host=self.host, port=self.port, db=self.db)

    # def connect(self):
    #     self.client = redis.Redis(host=self.host, port=self.port, db=self.db)

    def set(self, key, value, ttl=None):
        """
        Store a key-value pair with optional TTL (time-to-live).
        """
        self.client.set(key, value, ex=ttl)

    def get(self, key):
        """
        Retrieve a value by its key.
        """
        return self.client.get(key)

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
