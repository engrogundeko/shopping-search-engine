from dataclasses import dataclass
from typing import List, Dict, Optional, Literal, Any
from asyncio import to_thread

from config import GEMINI_API_KEY, REDIS_PASSWORD
from providers.config import get_all_results
from schema import ContentSchema
from .base import QueryEngineBase
from redis import Redis

from langchain.docstore.document import Document
from redisvl.query.filter import FilterExpression
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank
from langchain_community.vectorstores import FAISS


class QueryEngine(QueryEngineBase):
    """
    Search engine implementation supporting multiple search modes.
    """ 

    def __init__(self):
        # Placeholder for indexing and models
        self.index = []
        self.redis_url: str = "redis://localhost:6379"
        self.host = "redis-10198.c228.us-central1-1.gce.redns.redis-cloud.com"
        self.port = 10198
        self.index_name: str = "search_index"
        self.embedding_model: str = "models/embedding-001"
        self.metadata_schema: Optional[List[Dict[str, Any]]] = None
        self.embedding_model: str = "models/embedding-001"
        self.embeddings = self.__load_embeddings()
        self.redis = Redis(host=self.host, port=self.port, username="default", password=REDIS_PASSWORD)
        self.vectorstore_config = self.__get_redis_config()
        self.vectorstore: Optional[RedisVectorStore] = None
        self.documents = []

    def __get_redis_config(self):
        return RedisConfig(
            redis_client=self.redis,
            index_name=self.index_name, 
            metadata_schema=self.metadata_schema, 
            embedding_model=self.embedding_model
            )

    def __load_embeddings(self):
        return GoogleGenerativeAIEmbeddings(
            model=self.embedding_model, 
            google_api_key=GEMINI_API_KEY
            )

    async def aload_contents(self, contents: ContentSchema) -> Any:
        self.documents = []
        for content_dict in contents.contents:  
            # Use 'result' key for the TextSchema
            if content_dict:
                # Sanitize metadata to ensure Redis-compatible types
                sanitized_metadata = {}
                for key, value in content_dict.metadata.items():
                    # Convert lists to comma-separated strings
                    if isinstance(value, list):
                        value = ','.join(str(v) for v in value)
                    # Convert other non-string types to strings
                    elif not isinstance(value, (str, int, float, bool)):
                        value = str(value)
                    
                    # Ensure key is a string
                    sanitized_metadata[str(key)] = value

                # Create Document with sanitized metadata
                self.documents.append(
                    Document(
                            page_content=content_dict.text, 
                        metadata=sanitized_metadata
                    )
                )

        # If no documents were created, add a default document
        if not self.documents:
            self.documents.append(
                Document(page_content="No content available", metadata={"source": "default"})
            )

        # Fallback to in-memory storage if Redis is not available
        try:
            self.vector_store = await to_thread(
                RedisVectorStore.from_documents,
                documents=self.documents,
                embedding=self.embeddings,
                config=self.vectorstore_config
            )
        except Exception as e:
            print(f"Redis connection failed: {e}")
            print("Falling back to in-memory vector storage")
            # Use FAISS as a fallback
            self.vector_store = await to_thread(
                FAISS.from_documents,
                documents=self.documents,
                embedding=self.embeddings
            )

        return self.vector_store
    
    def keyword_retriever(self):
        """Perform a simple keyword-based search."""
        return BM25Retriever.from_documents(self.documents)


    def rerank(
        self, 
        mode: Literal["fast", "balanced", "quality"], 
        query: str, 
        retriever, 
        k: int = 5
        ) -> List[Document]:
        """Rerank results based on relevance."""
        model = "ms-marco-TinyBERT-L-2-v2"  # Default to fast mode model
        if mode == "balanced":
            model = "ms-marco-MiniLM-L-12-v2"
        elif mode == "quality":
            k=k+5
            # model = "rank-T5-flan"
        
        compressor = FlashrankRerank(model, top_n=k)
        compressor_retriever = ContextualCompressionRetriever(
            retriever=retriever,
            compressor=compressor
        )
        return compressor_retriever.invoke(query)


    async def asearch(
        self, 
        search_query: str, 
        query: str, 
        mode: str = 'quality', 
        metadata: dict = None, 
        k: int = 5
        ):
        """
        Perform a search with optional metadata filtering.
        """
        results = await get_all_results(search_query)
        await self.aload_contents(results)

        # Define metadata filter (if provided)
        metadata_filter = None
        if metadata:
            metadata_filter = FilterExpression(
                key=list(metadata.keys())[0],  # Assuming single key-value pair for simplicity
                operator="==",
                value=list(metadata.values())[0]
            )

        if mode == 'fast':
            retriever = self.keyword_retriever()
            docs = retriever.invoke(query)
        elif mode == 'balanced':
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": k, "filter": metadata_filter})
            docs = retriever.invoke(query)
        elif mode == 'quality':
            retriever = EnsembleRetriever(
                retrievers=[
                    self.vectorstore.as_retriever(search_kwargs={"k": k, "filter": metadata_filter}),
                    self.keyword_retriever()
                ],
                weights=[0.5, 0.5]
            )
            docs = retriever.invoke(query)
        else:
            raise ValueError("Invalid mode. Choose 'fast', 'balanced', or 'quality'.")

        # Convert documents to dictionaries
        # self.vector_store.delete
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
