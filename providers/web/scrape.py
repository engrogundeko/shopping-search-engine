import asyncio
from typing import List, Dict, TypeVar

from utils.logging import logger
from config import USER_AGENT

from aiohttp import ClientSession, ClientTimeout

from langchain_community.document_loaders import AsyncHtmlLoader, AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer, Html2TextTransformer
from langchain.schema import Document

from pydantic import BaseModel


T = TypeVar('T', bound=BaseModel)


class AsyncWebScraper:
    def __init__(
        self, 
        no_words: int = 500,
        schema: T = None,
        ) -> None:
        """
        Initialize the scraper with optional URLs.
        """
        self.no_words = no_words
        self.soup_transformer = BeautifulSoupTransformer()
        self.html2text_transformer = Html2TextTransformer()
        self.schema = schema
        self.header = {"User-Agent": USER_AGENT}


    async def fetch_html(self, urls: List[str]) -> List[Document]:
        """
        Fetch HTML for static web pages.
        """
        loader = AsyncHtmlLoader(urls, verify_ssl=False, header_template=self.header)
        return await loader.aload()

    async def fetch_html_js(self, urls: List[str]) -> List[Document]:
        """
        Fetch HTML for dynamic web pages (with JavaScript rendering).
        """
        loader = AsyncChromiumLoader(urls)
        return await loader.aload()

    def extract_content(self, docs: List[Document], tags: List[str] = None) -> Dict[str, List[str]]:
        """
        Extract content from specific HTML tags using BeautifulSoupTransformer.
        """
        transformed_docs = self.soup_transformer.transform_documents(docs, tags_to_extract=tags)
        return transformed_docs
        # return {doc.metadata['source']: doc.page_content[:self.no_words] for doc in transformed_docs}

    def extract_text(self, docs: List[Document]) -> Dict[str, str]:
        """
        Extract plain text from HTML using Html2TextTransformer.
        """
        transformed_docs = self.html2text_transformer.transform_documents(docs)
        return transformed_docs
        # return WebResultDict(metadata=scraped_data.metadata, content=scraped_data.page_content)
        
    async def scrape(
        self,
        urls: List[str],
        timeout: int = 5,
        retries=3,
        rate_limit=4,
        ignore_errors=True,
        use_js: bool = False,
        tags: List[str] = None,
        plain_text: bool = False
    ) ->List[Document]:
        """
        Scrape websites and extract content based on tags or plain text.

        :param urls: List of URLs to scrape.
        :param use_js: Use JavaScript-enabled scraping if True.
        :param tags: List of tags to extract content from (if plain_text is False).
        :param plain_text: Extract plain text instead of tag-based content if True.
        :return: Extracted content as a dictionary.
        """
        if use_js:
            docs = await self.fetch_html_js(urls)
        else:
            docs = await self.scrape_websites(
                urls, timeout, retries, rate_limit, ignore_errors)
        
        if plain_text:
            return self.extract_text(docs)

        return self.extract_content(docs, tags)



    async def scrape_websites(
        self,
        urls: List[str],
        timeout: int = 10,  
        retries: int = 3,   
        rate_limit: int = 5, 
        ignore_errors: bool = True
    ) -> List[Document]:
        """
        Scrape websites asynchronously with error and timeout handling.

        Args:
            urls (List[str]): List of URLs to scrape.
            timeout (int): Timeout for each request in seconds.
            retries (int): Number of retries for failed requests.
            rate_limit (int): Max number of concurrent requests.
            ignore_errors (bool): Whether to ignore errors and continue.

        Returns:
            List[Document]: Successfully scraped documents.
        """
        async def fetch(url: str, session: ClientSession, attempt: int = 1) -> Document:
            try:
                async with session.get(url, timeout=ClientTimeout(total=timeout)) as response:
                    text = await response.text()
                    loader = AsyncHtmlLoader(web_path=url)  
                    return loader._to_document(url, text)
            except Exception as e:
                if attempt < retries:
                    return await fetch(url, session, attempt + 1)
                if not ignore_errors:
                    raise e
                logger.info(f"Failed to fetch {url} after {retries} attempts: {e}")
                return None

        semaphore = asyncio.Semaphore(rate_limit)

        async def fetch_with_limit(url: str, session: ClientSession):
            async with semaphore:
                return await fetch(url, session)

        async with ClientSession() as session:
            tasks = [fetch_with_limit(url, session) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None results and return only successful documents
        return [result for result in results if isinstance(result, Document) and result.page_content]

