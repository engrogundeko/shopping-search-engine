from .redis import RedisCache
from .memcached import MemcachedCache

class CacheManager:
    """
    High-level cache manager to switch between Redis and Memcached backends.
    """

    def __init__(self, backend='redis', **kwargs):
        self.backend = backend
        if backend == 'redis':
            self.cache = RedisCache(**kwargs)
        elif backend == 'memcached':
            self.cache = MemcachedCache(**kwargs)
        else:
            raise ValueError("Unsupported cache backend. Use 'redis' or 'memcached'.")
        
        self.cache.connect()

    def set(self, key, value, ttl=None):
        """
        Set a key-value pair in the cache.
        """
        self.cache.set(key, value, ttl)

    def get(self, key):
        """
        Get a value from the cache by its key.
        """
        return self.cache.get(key)

    def delete(self, key):
        """
        Delete a key from the cache.
        """
        self.cache.delete(key)

    def clear(self):
        """
        Clear all keys from the cache.
        """
        self.cache.clear()
