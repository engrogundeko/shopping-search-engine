from abc import ABC, abstractmethod

class QueryEngineBase(ABC):
    """
    Abstract base class for search engines.
    """

    @abstractmethod
    def aload_contents(self, query):
        """Perform a keyword-based search."""
        pass

    @abstractmethod
    def keyword_retriever(self, query):
        """Perform a semantic-based search."""
        pass

    @abstractmethod
    def rerank(self, results, query):
        """Rerank the search results based on relevance."""
        pass

    @abstractmethod
    def asearch(self, query, mode='quality'):
        """
        Perform a search using the specified mode:
        - 'fast': Use keyword search.
        - 'balance': Combine keyword and semantic search.
        - 'quality': Perform full search with reranking.
        """
        pass
