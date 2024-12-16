from dataclasses import dataclass
from typing import List, Dict, Optional, Literal

from ...config import GEMINI_API_KEY
from ...providers.config import get_all_results
from .base import QueryEngineBase

from langchain.docstore.document import Document
from redisvl.query.filter import FilterExpression
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank


class QueryEngine(QueryEngineBase):
    """
    Search engine implementation supporting multiple search modes.
    """ 

    def __init__(self):
        # Placeholder for indexing and models
        self.index = []
        self.redis_url: str = "redis://localhost:6379"
        self.index_name: str = "search_index"
        self.embedding_model: str = "models/embedding-001"
        self.metadata_schema: Optional[List[Dict[str, Any]]] = None
        self.embedding_model: str = "models/embedding-001"
        self.embeddings = self.__load_embeddings()
        self.vectorstore_config = self.__get_redis_config()
        self.vectorstore: Optional[RedisVectorStore] = None
        self.documents = []

    def __get_redis_config(self):
        return RedisConfig(
            redis_url=self.redis_url, 
            index_name=self.index_name, 
            metadata_schema=self.metadata_schema, 
            embedding_model=self.embedding_model
            )


    def __load_embeddings(self):
        return GoogleGenerativeAIEmbeddings(
            model=self.embedding_model, 
            google_api_key=GEMINI_API_KEY
            )

    async def aload_contents(self, contents: ContentSchema) -> RedisVectorStore:
        self.documents = []
        for content_dict in contents.contents:  
            for _, text_schema in content_dict.items():  
                metadata = text_schema.metadata  
                text = text_schema.text  
                self.documents.append(Document(page_content=text, metadata=metadata))

        self.vectorstore = await RedisVectorStore.afrom_documents(
            documents=self.documents, 
            config=self.vectorstore_config
        )
        return self.vectorstore
        

    def keyword_retriever(self):
        """Perform a simple keyword-based search."""
        return BM25Retriever.from_documents(self.documents)


    # def similarity_search(self, query, k=5, filter: FilterExpression = None):
    #     """Perform a semantic-based search."""
    #     results = self.vectorstore.similarity_search(query, k, filter)
    #     return results

    # def hybrid_search(self, query, metadata: dict = None) -> List[Document]:
    #     """Perform a hybrid-based search."""
    #     retriever_vectordb = self.vectorstore.as_retriever(search_kwargs={"k": 5})

    #     hybrid_retriever = EnsembleRetriever(
    #         retrievers=[retriever_vectordb, self.keyword_retriever()], weights=[0.5, 0.5]
    #     )
    #     docs_rel = hybrid_retriever.get_relevant_documents(query, metadata)

    #     return docs_rel

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
            model = "rank-T5-flan"
        
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
            docs = retriever.get_relevant_documents(query)
        elif mode == 'balanced':
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": k, "filter": metadata_filter})
            docs = retriever.get_relevant_documents(query)
        elif mode == 'quality':
            retriever = EnsembleRetriever(
                retrievers=[
                    self.vectorstore.as_retriever(search_kwargs={"k": k, "filter": metadata_filter}),
                    self.keyword_retriever()
                ],
                weights=[0.5, 0.5]
            )
            docs = retriever.get_relevant_documents(query)
        else:
            raise ValueError("Invalid mode. Choose 'fast', 'balanced', or 'quality'.")

        # Convert documents to dictionaries
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
