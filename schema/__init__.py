import json
from typing import List
from dataclasses import dataclass

from .product import ProductSchema
from .price import PriceDetailSchema
from .seller import SellerDetailSchema
from .specification import SpecificationsSchema
from .search import TextSchema, ContentSchema
from .review import ReviewSchema, ReviewsResponseSchema

@dataclass
class ProductResponseSchema:
    prices: PriceDetailSchema | None = None
    seller: SellerDetailSchema | None = None
    specifications: SpecificationsSchema | None = None
    reviews: ReviewsResponseSchema | None = None
    product:  ProductSchema | None = None

@dataclass
class MetadateSchema:
    query: str
    total_results: int
    sources: List[str]
    execution_time_ms: int


@dataclass
class ShopProviderResponse:
    shop_name: str
    results: List[ProductResponseSchema]
    # all_prices: List[str] | None= field(default_factory=list)

    def to_dict(self):
        def convert(obj):
            if isinstance(obj, list):
                return [convert(item) for item in obj]
            elif hasattr(obj, "__dict__"):
                return {key: convert(value) for key, value in obj.__dict__.items()}
            else:
                return obj

        result = {}

        if isinstance(self, list):
            result[self[0].__class__.__name__.lower()] = [convert(item) for item in self]
        elif hasattr(self, "__dict__"):
            result[self.__class__.__name__.lower()] = convert(self)
        else:
            result[str(self)] = self
        return result

    def to_json(self):
        with open("output.json", "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def to_text(self):
        pass

    def parse_search_results(self):
        items = []  # This list will store the final results
        # Check if the input is a dictionary with 'results' key
        result_dict = self.to_dict()["shopproviderresponse"]
        results = result_dict["results"]
        for product in results:
            try:
                # Safely extract product information with default values
                title = product.get('prices', {}).get('name', 'Unknown Product')
                discount = product.get('prices', {}).get('discount', '0%')
                price = product.get('prices', {}).get('current_price', 'N/A')
                old_price = product.get('prices', {}).get('old_price', 'N/A')

                # Safely extract features, categories, and box contents
                specifications = product.get('specifications', {})
                product_info = product.get('product', {})
                
                features = '\n'.join([f"- {feature}" for feature in specifications.get('key_features', [])])
                categories = '\n'.join([f"- {category}" for category in product_info.get('categories', [])])
                box_contents = '\n'.join([f"- {item}" for item in specifications.get('box_contents', [])])
                
                image_url = product_info.get('image_url', [])
                product_url = product.get('prices', {}).get('product_url', '')

                # Construct the semantic-rich markdown for each product
                markdown = f"""# Product Information

                ## Features
                - **Name:** {title}
                - **Description:** {product_info.get('description', 'No description available')}
                - **Brand:** {product_info.get('brand', 'Unknown')}
                - **Categories:**\n{categories}
                - **Key Features:**\n{features}
                - **Box Contents:**\n{box_contents}
                """

                metadata = {
                            "title": title,
                            "price": price,
                            "discount": discount,
                            "product_url": product_url,
                            "image_url": image_url
                        }
                items.append(TextSchema(text=markdown, metadata=metadata))
            except Exception as e:
                print(f"Error processing product: {e}")
                continue

        contents = ContentSchema(contents=items)
        return contents


@dataclass
class ResponseSchema:
    results: List[ShopProviderResponse]
    metadata: MetadateSchema


__all__ = [
    "PriceDetailSchema",
    "PriceMetadataSchema",
    "PriceResponseSchema",
    "SentimentSummarySchema",
    "SentimentDetailSchema",
    "SentimentMetadataSchema",
    "SentimentResponseSchema",
    "ReviewSchema",
    "ReviewsMetadataSchema",
    "ReviewsResponseSchema",
    "SellerDetailSchema",
    "SellersMetadataSchema",
    "SellersResponseSchema",
    "SpecificationsSchema",
    "ShopProviderSchema",
    "ResponseSchema",
    "ShopProviderResponse",
    "MetadateSchema"

]