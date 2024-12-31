import typing
import asyncio

from langchain import retrievers
from config import GEMINI_API_KEY, GROQ_API_KEY
from dataclasses import dataclass

from .searxng import SearxNGSearchTool
from .scrape import AsyncWebScraper
from .prompt import information_extractor_prompt
from utils.decourator import async_retry
from utils.logging import logger

import httpx
from pydantic_ai import Agent   
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter


from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain.retrievers import EnsembleRetriever
# from langchain_community.retrievers import BM25Retriever
from langchain.docstore.document import Document
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank

class WebResultDict(typing.TypedDict):
    metadata: dict
    content: str


class ResultSchema(BaseModel):
    content: str
    valid: bool


@dataclass
class Dependencies:
    api_key = GEMINI_API_KEY
    http_client = httpx.AsyncClient


class AsyncWebManager:
    def __init__(
        self, 
        cache_ttl: int = 3600, 
        chunk_size=1000, 
        chunk_overlap=200, 
        word_threshold=5000
        ):
            
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.threshold = word_threshold
        self.n_load = 20
        self.embedding_model: str = "models/embedding-001"
        self.searxng = SearxNGSearchTool()
        self.scraper = AsyncWebScraper()
        self.embeddings = self._load_embeddings()

        # self.llm = Agent(
        #     result_type=ResultSchema,
        #     model="gemini-2.0-flash-exp",
        #     name="Web Content Extractor",
        #     system_prompt=information_extractor_prompt,
        #     deps_type=Dependencies,
        # )

    def _load_embeddings(self):
        return GoogleGenerativeAIEmbeddings(
            model=self.embedding_model, 
            google_api_key=GEMINI_API_KEY
            )

    async def load_contents(self, k, documents: typing.List[Document]):
        logger.info(f"Number of documents to load: {len(documents)}")
        try:
            vectorstore = await asyncio.to_thread(
                FAISS.from_documents,
                documents=documents,
                embedding=self.embeddings
            )
            logger.info("FAISS vectorstore created successfully.")
            return vectorstore.as_retriever(search_kwargs={"k": k})
        except Exception as e:
            logger.error(f"Error creating FAISS vectorstore: {e}")
            raise

    async def rerank(
        self, 
        mode: typing.Literal["fast", "balanced", "quality"], 
        query: str, 
        retriever, 
        k: int = 5
        ) -> typing.List[Document]:
        """Rerank results based on relevance."""
        model = "ms-marco-TinyBERT-L-2-v2"  # Default to fast mode model
        if mode == "balanced":
            model = "ms-marco-MiniLM-L-12-v2"
        elif mode == "quality":
            k=k+5
            # model = "rank-T5-flan"
        
        compressor = FlashrankRerank(model=model, top_n=k)
        compressor_retriever = ContextualCompressionRetriever(
            base_retriever=retriever,
            base_compressor=compressor
        )
        return await compressor_retriever.ainvoke(query)

        
    async def insights_search(self, query, mode, search_results: typing.List[Document]) -> typing.List[WebResultDict]:
        search_urls = [r.metadata["link"] for r in search_results]
        scraped_data = await self.scraper.scrape(search_urls, plain_text=True)

        # Summarize or filter large scraped content
        summarized_data = []
        for doc in scraped_data:
            if len(doc.page_content) > self.threshold:  # Example threshold
                summarized_data.append(
                    Document(
                        page_content=doc.page_content[:self.threshold],
                        metadata=doc.metadata
                    )
                )
                # summarized_data.append({"content": doc["content"][:5000], **doc})  # Truncate or summarize
            else:
                summarized_data.append(doc)
        
        splits = self.chunk_content(summarized_data)
        retriever = await self.load_contents(40, splits)
        reranked_results = await self.rerank(mode, query, retriever, 20)

        return [
            WebResultDict(metadata=r.metadata, content=r.page_content) for r in reranked_results
        ]
 

    def chunk_content(self, search_results: typing.List[Document]):
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=self.chunk_size,
        chunk_overlap=self.chunk_overlap
        )
        splits = splitter.split_documents(search_results)
        return splits


    @async_retry(retries=5, delay=1.0)
    async def search(
        self, 
        mode: typing.Literal["fast", "balanced", "quality"],
        search_query: str,
        search_type: typing.Literal["insights", "comparison", "web", "review"],
        filter: dict = None,
        n_k: int = 5,
        description: str = None
        ):
        k=20
        search_results = await self.searxng.search(search_query, k)

        retrieval = await self.load_contents(k, search_results)
        results = await self.rerank(
            mode=mode, 
            query=search_query, 
            retriever=retrieval, 
            k=n_k
            )

        if search_type == "insights":
            return await self.insights_search(search_query, mode, results)


    # async def extract_content(self, search_results: typing.List[Document])-> typing.List[WebResultDict]:
    #     results = []
    #     for search_result in search_results:
    #         web_content = f"""
    #             Web Content: {search_result.page_content}
    #             """
    #         try:
    #             content = await self.llm.run(web_content)
    #             data = content.data
    #             if data.valid is False:
    #                 continue

    #             results.append(
    #                 WebResultDict(metadata=search_result.metadata, content=data.content
    #                 )
    #             )
   
    #             await asyncio.sleep(0.5)
    #         except Exception as e:
    #             logger.error(f"Error extracting content: {e}")
    #             continue

    #     return results

web_manager = AsyncWebManager()