from typing import List, Dict, Any, Optional

from ..config import get_settings

from langchain_redis import RedisConfig, RedisVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document

class VectorStore:
    def __init__(
        self, 
        redis_url: str = "redis://localhost:6379",
        index_name: str = "search_index",
        metadata_schema: Optional[List[Dict[str, Any]]] = None,
        embedding_model: str = "models/embedding-001"
    ):
        """
        Helper class to manage RedisVectorStore interactions.

        Args:
            redis_url (str): Redis connection URL.
            index_name (str): Name of the index to use in Redis.
            metadata_schema (Optional[List[Dict[str, Any]]]): Schema for metadata.
            embedding_model (str): Embedding model to use for vectorization.
        """
        self.redis_url = redis_url
        self.index_name = index_name
        self.metadata_schema = metadata_schema or []
        self.embeddings = self.load_embeddings()
        self.config = self.__load_config()
        self.vector_store = RedisVectorStore(self.embeddings, config=self.config)

    def __load_config(self) -> RedisConfig:
        return RedisConfig(
            index_name=self.index_name,
            redis_url=self.redis_url,
            metadata_schema=self.metadata_schema,
        )

    def load_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        return GoogleGenerativeAIEmbeddings(
            model=self.embeddings, 
            api_key=get_settings().GEMINI_API_KEY)
        

    async def add_documents(
        self, 
        texts: List[str], 
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Add texts to the Redis vector store.

        Args:
            texts (List[str]): List of texts to add.
            metadata (Optional[List[Dict[str, Any]]]): Corresponding metadata for the texts.

        Returns:
            List[str]: List of IDs for the added texts.
        """
        return await self.vector_store.afrom_texts(texts, self.embeddings, metadatas=metadata)

    async def delete_by_ids(self, ids: List[str]) -> int:
        """
        Delete documents from the vector store by their IDs.

        Args:
            ids (List[str]): List of IDs to delete.

        Returns:
            int: Number of deleted items.
        """
        return await self.vector_store.index.drop_keys(ids)

    async def similarity_search(self, query: str, k: int = 2) -> List[Document]:
        """
        Perform a similarity search.

        Args:
            query (str): Query text.
            k (int): Number of results to return.

        Returns:
            List[Document]: List of documents matching the query.
        """
        return await self.vector_store.similarity_search(query, k)

    async def similarity_search_with_score(self, query: str, k: int = 2) -> List[Dict[str, Any]]:
        """
        Perform a similarity search with scores.

        Args:
            query (str): Query text.
            k (int): Number of results to return.

        Returns:
            List[Dict[str, Any]]: List of documents with scores.
        """
        results = await self.vector_store.similarity_search_with_score(query, k)
        return [{"document": doc, "score": score} for doc, score in results]

    async def as_retriever(self, search_type: str = "similarity", search_kwargs: Optional[Dict[str, Any]] = None):
        """
        Transform the vector store into a retriever.

        Args:
            search_type (str): Search type (default is "similarity").
            search_kwargs (Optional[Dict[str, Any]]): Additional search parameters.

        Returns:
            Retriever: A retriever object.
        """
        search_kwargs = search_kwargs or {"k": 2}
        return await self.vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

    async def clear_store(self):
        """
        Clear all entries in the vector store.

        Returns:
            None
        """
        await self.vector_store.index.drop_index()

# Example usage:
if __name__ == "__main__":
    import asyncio

    async def main():
        helper = RedisVectorStore(
            redis_url="redis://localhost:6379",
            index_name="newsgroups",
            metadata_schema=[{"name": "category", "type": "tag"}],
            embedding_model="text-embedding-ada-002"
        )

        texts = ["Space exploration is fascinating.", "Atheism is a philosophical stance."]
        metadata = [{"category": "sci.space"}, {"category": "alt.atheism"}]

        # Add texts to vector store
        ids = await helper.add_texts(texts, metadata)
        print("Added IDs:", ids)

        # Query the vector store
        results = await helper.similarity_search("Tell me about space.")
        for doc in results:
            print("Content:", doc.page_content)
            print("Metadata:", doc.metadata)

    asyncio.run(main())
