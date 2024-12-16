from calendar import c
from locale import currency
import os
import json
import asyncio
import re
from typing import List
from pprint import pprint

from .utils import get_affiliate_link
# from searchEngine.schema.price import PriceDetailSchema
# from searchEngine.schema.product import ProductSchema
from ...schema import (
    ProductResponseSchema, 
    SellerDetailSchema, 
    ShopProviderResponse, 
    PriceDetailSchema,
    ReviewSchema,
    SpecificationsSchema,
    ProductSchema,
    ReviewsResponseSchema
)
from .schema import Product, ProductData, Image
from ..ranker import rank_search_results
from pydantic import ValidationError

from .. import ShopEngine


class ShopInverse(ShopEngine):
    def __init__(self, search_query):
        super().__init__(search_query)
        self.url = "https://shopinverse.com/"
        self.filename = "shopinverse.json"
        
        # await self.update_product_data()

    async def initialize_data(self):
        if not os.path.exists(self.filename):
            self.product_data = await self.fetch_data()
            with open(self.filename, "w") as f:
                json.dump(self.product_data, f, indent=4)
        else:
            with open(self.filename, "r") as f:
                self.product_data = json.load(f)

    async def fetch_data(self, limit=250, page=1):
        # Append '.json' to the URL to get the product data
        if not self.url.endswith('.json'):
            shopify_url = self.url.rstrip('/') + '/products.json'

        # Make the HTTP request to fetch the JSON data
        products = []
        while True:
            params = {'limit': limit, 'page': page}
            response = await self.client.get(shopify_url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

            # Parse the JSON response
            product_data = response.json()
            if "products" in product_data and product_data["products"]:
                products.extend(product_data["products"])
                page += 1
            else:
                break 
        return products

    async def update_product_data(self):
        while True:
            await asyncio.sleep(24 * 60 * 60)
            self.product_data = await self.fetch_data()
            with open(self.filename, "w") as f:
                json.dump(self.product_data, f, indent=4)


    async def search(self, keyword: str):
        """
        Search for products that match a given keyword in their title or description.

        Args:
            product_data (dict): The JSON data containing Shopify product information.
            keyword (str): The keyword to search for.

        Returns:
            list: A list of matching products.
        """
        keyword_pattern = re.compile(keyword, re.IGNORECASE)  # Compile regex for case-insensitive search
        matching_products = []
        rank_list = []

        for product in self.product_data:
            title = product.get("title", "")
            description = product.get("body_html", "")

            if keyword_pattern.search(title) or keyword_pattern.search(description):
                matching_products.append(product)
                rank_list.append({"name": title})
                
        # if matching_products:
        #     # results = await rank_search_results(rank_list[:10], keyword) 
        #     new_results = []
        #     for match in matching_products:
        #         for r in results:
        #             d = r.__dict__
        #             if match["title"] == d["name"]:
        #                 new_results.append(match)

        # else:
        #     return {
        #         "shop_name": "ShopInverse",
        #         "results": []
        #     }

        try:
            dt = {"products": matching_products}
            product_data = ProductData.model_validate(dt)
            # print(product_data)
            validated_product_data = self.convert(product_data.products)
            return validated_product_data
        
        except ValidationError as e:
            print(f"Validation error: {e}")
            return {
                "shop_name": "ShopInverse",
                "results": []
            }

    def convert(self, product_data: Product):
        all = []
        for product in product_data:
            p: Product = product
            print(p)
            images: List[Image] =[i.src for i in p.images]
            prd = ProductSchema(
                name=p.title, 
                brand=p.vendor, 
                image_url=images,
                price=p.variants[0].price, 
                categories=list(p.product_type)
                )
            url = self.url + "products/" + p.handle
            pr = PriceDetailSchema(
                name=p.title,
                product_url=url,
                current_price=p.variants[0].price,
                currency="NGN",
                product_affiliate_url=get_affiliate_link(url),
                product_id=p.id

                )


            p = ProductResponseSchema(
                seller=SellerDetailSchema(),
                reviews=ReviewsResponseSchema(reviews=[ReviewSchema()]),
                product=prd,
                prices=pr,
                specifications=SpecificationsSchema(p.body_html)
            )
            all.append(p)

            # for var in p.variants:
            #     url = self.url + "products/" + var.handle
            #     prd = ProductSchema(
            #         name=var.title, 
            #         brand=p.vendor, 
            #         price=var.price,
            #         image_url=self.__get_image(var.id, p), 
            #         categories=list(p.product_type),
            #         currency="NGN"
            #         )
            #     pr = PriceDetailSchema(
            #     name=var.title,
            #     product_url=url,
            #     product_affiliate_url=get_affiliate_link(url),
            #     product_id=var.id,
            #     current_price=var.price,
            #     currency="NGN"
            #     )

            #     p = ProductResponseSchema(
            #     seller=SellerDetailSchema(),
            #     reviews=ReviewsResponseSchema(reviews=[ReviewSchema()],
            #     product=prd,
            #     prices=pr
            #     ))
            #     all.append(p)

            # p = ProductResponseSchema(
            #     name="ShopInverse",
            #     seller_details=all_spec,
            #     reviews=all_r,
            #     product_details=all_prd,
            #     price_details=all_p
            # )
        return ShopProviderResponse(
            shop_name="ShopInverse",
            results=all
        )

    def __get_image(self, variant_id, p):
        images = p['images']
        for i in images:
            k = [str(v) for v in i['variant_ids']]
            if str(variant_id) in k:
                return i['src']


    async def run(self):
        await self.initialize_data()
        results = await self.search(self.search_query)

        return results

# async def main():
#     query = "Lenovo"
#     shop_inverse = ShopInverse(query)
#     await shop_inverse.initialize_data()
#     results = await shop_inverse.search(query)
#     pprint(results)
#     print("\n\n ==================== \n\n")

# if __name__ == "__main__":
#     asyncio.run(main())
