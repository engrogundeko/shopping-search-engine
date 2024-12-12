from typing import List
from dataclasses import dataclass, field
import json

from .price import PriceDetailSchema
from .seller import SellerDetailSchema
from .specification import SpecificationsSchema
from .review import ReviewSchema, ReviewsResponseSchema
from .product import ProductSchema


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
    all_prices: List[str] | None= field(default_factory=list)

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