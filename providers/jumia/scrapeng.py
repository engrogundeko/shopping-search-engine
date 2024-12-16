import asyncio
from urllib.parse import quote_plus
from typing import List

import httpx
from bs4 import BeautifulSoup 

from .utils import (
    extract_reviews,
    extract_seller_information,
    extract_specifications, 
    extract_product_data,
    parse_price,
    parse_discount
    )
from ...schema import (
    SellerDetailSchema, 
    ProductResponseSchema,
    ShopProviderResponse,
    SpecificationsSchema,
    ReviewsResponseSchema,
    PriceDetailSchema,
    ProductSchema
)
from .. import ShopEngine
# from .agent import rank_search_results

class JumiaScraperNG(ShopEngine):
    def __init__(self, search_query):
        super().__init__(search_query)
        self.url = "https://www.jumia.com.ng/"


    def extract_product_id(self, product_url) -> List[PriceDetailSchema]:
        """
        Extract the product ID from a Jumia product URL.
        :param product_url: The URL of the product.
        :return: The product ID as a string.
        """
        try:
            return product_url.split('-')[-1].split('.')[0]
        except IndexError:
            return None


    async def parse_page(self, page_source):
        """
        Parse the HTML page source to extract product information.
        :param page_source: HTML content of the page.
        :return: List of products with their details.
        """
        products = []
        self.re_rank_list = []
        soup = BeautifulSoup(page_source, features="html.parser")
        # data = soup.find_all('div', class_='-pvs col12')
        products_container = soup.find_all('article', class_='prd')
        for id, product_container in enumerate(products_container):
            product = {}
            product['product_id'] = product_container.find('a', {'data-sku': True})['data-sku']
            # product['product_link'] = product_container.find('a', class_='core')['href']
            product['name'] = product_container.find('h3', class_='name').text.strip()
            product['current_price'] = product_container.find('div', class_='prc').text.strip()
            product['old_price'] = product_container.find('div', class_='old').text.strip() if product_container.find('div', class_='old') else "Not Available"
            product['discount'] = product_container.find('div', class_='bdg _dsct _sm').text.strip() if product_container.find('div', class_='bdg _dsct _sm') else "No Discount"
            product['product_url'] = self.url + product_container.find('a', class_='core')['href']
            product['currency'] = "NGN"
            try:
                product['current_price'] = parse_price(product['current_price'])
                product['old_price'] = parse_price(product['old_price'])
                product['discount'] = parse_discount(product['discount'])
            except ValueError:
                continue

            product_detail = PriceDetailSchema(**product)
            products.append(product_detail)
            if id > 10:
                break
    

            # self.re_rank_list.append(product['name'])

        self.search_results.extend(products)
        # self.search_results = await rank_search_results(self.re_rank_list, self.search_query, self.search_results)
        return self.search_results

    async def fetch_page(self, url) -> PriceDetailSchema:
        """
        Fetch a single page using httpx.
        :param url: URL of the page to fetch.
        :return: HTML content of the page.
        """
        try:
            response = await self.client.get(url)
            # print("======================================", response)
            response.raise_for_status()
            return response.text
        except httpx.RequestError as e:
            print(f"Error fetching {url}: {e}")
            return None
            # 
    async def fetch_and_parse_page(self, url: str) -> List:
        content = await self.fetch_page(url)
        return await self.parse_page(content)

    async def search(self, num_pages=1) -> List:
        encoded_query = quote_plus(self.search_query)
        tasks = []

        # Create tasks for fetching and parsing pages
        for i in range(1, num_pages + 1):
            url = f"{self.url}catalog/?q={encoded_query}&page={i}"
            print(f"Scheduling fetch for page {i}")
            tasks.append(self.fetch_and_parse_page(url))

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks)

        # Flatten the list of items from all pages
        items = [item for sublist in results for item in sublist]
        return items


    async def parse_detailed_product(self, product_url) -> BeautifulSoup:
        """
        Parse the HTML page source to extract product information.
        :param page_source: HTML content of the page.
        :return: List of products with their details.
        """
        if product_url in self.cache:
            return self.cache[product_url]
        response = await self.client.get(product_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, features="html.parser")
        self.cache[product_url] = soup

        return soup

    async def get_review_product(self, product_url: str) -> ReviewsResponseSchema: 
        soup = await self.parse_detailed_product(product_url)
        return extract_reviews(soup)

    async def get_specification_product(self, product_url: str) -> SpecificationsSchema: 
        soup = await self.parse_detailed_product(product_url)
        return extract_specifications(soup)

    async def get_product(self, product_url: str) -> ProductSchema: 
        soup = await self.parse_detailed_product(product_url)
        return extract_product_data(soup)

    async def get_seller(self, product_url: str) -> SellerDetailSchema: 
        soup = await self.parse_detailed_product(product_url)
        content = extract_seller_information(soup)
        if content:
            return content

    async def get_detailed_product(self, product_url: str) -> ProductResponseSchema:
        tasks = [       
            self.get_review_product(product_url),
            self.get_specification_product(product_url),
            self.get_seller(product_url),
            self.get_product(product_url),
        ]
        response = await asyncio.gather(*tasks)
       
        response = {
            "prices": self.get_price_product(product_url),
            "reviews": response[0],
            "specifications": response[1],
            "seller": response[2],
            "product": response[3]
        }
        response = ProductResponseSchema(**response)
        return response

    @property
    def get_all_prices(self)-> List[float]:
        return  [price.__dict__["current_price"] for price in self.search_results]
        
    def get_price_product(self, product_url):
        for price in self.search_results:
            if price.__dict__["product_url"] == product_url:
                return price

    async def run(self):
        try:
            re = await self.search()
        except Exception as e:
            print(f"Error occurred: {e}")
        print(f"Search results length: {len(self.search_results)}")
        
        if self.search_results:
            results = []
            for r in re:
                result = r.__dict__

                response = await self.get_detailed_product(result["product_url"])
                results.append(response)

            response = ShopProviderResponse(shop_name="JumiaNG", results=results)
            return response.parse_search_results()
        else:
            print("No search results found. Unable to get detailed product.")

    if __name__ == "__main__":  
        asyncio.run(main())
