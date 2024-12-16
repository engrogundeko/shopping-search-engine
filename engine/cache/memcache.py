import memcache

class MemcachedCache(CacheBase):
    """
    Memcached-based caching system.
    """

    def __init__(self, host='localhost', port=11211):
        self.host = host
        self.port = port
        self.client = None

    def connect(self):
        self.client = memcache.Client([(self.host, self.port)])

    def set(self, key, value, ttl=None):
        """
        Store a key-value pair with optional TTL (time-to-live).
        """
        self.client.set(key, value, time=ttl)

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
        self.client.flush_all()
