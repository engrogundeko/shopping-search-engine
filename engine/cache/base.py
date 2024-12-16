from abc import ABC, abstractmethod

class CacheBase(ABC):
    """
    Abstract base class for caching systems.
    Defines a common interface for Redis and Memcached caches.
    """

    # @abstractmethod
    # def connect(self):
    #     """Connect to the caching backend."""
    #     pass

    @abstractmethod
    def set(self, key, value, ttl=None):
        """Store a key-value pair in the cache."""
        pass

    @abstractmethod
    def get(self, key):
        """Retrieve a value by its key."""
        pass

    @abstractmethod
    def delete(self, key):
        """Delete a key from the cache."""
        pass

    @abstractmethod
    def clear(self):
        """Clear all keys from the cache."""
        pass
